from pathlib import Path
from typing import Dict
from agents import Agent, OpenAIChatCompletionsModel, Runner, ModelSettings


class AgentHandler:
    def __init__(
        self,
        *,
        vision_model: OpenAIChatCompletionsModel,
        language_model: OpenAIChatCompletionsModel,
        tools: Dict[str, callable],
        prompt_dir: Path,
        features_and_indicators: str,
    ) -> None:
        self._vision_model = vision_model
        self._language_model = language_model
        self._tools = tools
        self._prompt_dir = prompt_dir
        self._features_and_indicators = features_and_indicators

        self._agents: Dict[str, Agent] = {}

        self._create_agents()

    def _load_prompt(self, filename: str, **kwargs) -> str:
        path = self._prompt_dir / filename
        template = path.read_text(encoding="utf-8")
        return template.format(**kwargs)

    def _create_agents(self) -> None:
        """Create all agents once and cache them"""

        # Feature extraction agent (vision)
        self._agents["feature_extraction"] = Agent(
            name="feature_extraction",
            model=self._vision_model,
            instructions=self._load_prompt(
                "feature_extraction.md",
                features_and_indicators=self._features_and_indicators,
            ),
            model_settings=ModelSettings(temperature=0.4),
            tools=[],
        )

        # Interpretation agent (rules + reasoning)
        self._agents["interpretation"] = Agent(
            name="interpretation",
            model=self._language_model,
            instructions=self._load_prompt("interpretation.md"),
            model_settings=ModelSettings(temperature=0.5),
            tools=[
                self._tools["get_rule_information"],
                self._tools["similarity_search"],
            ],
        )

        # Chat / follow-up agent
        self._agents["chat"] = Agent(
            name="chat",
            model=self._language_model,
            instructions=self._load_prompt("chat.md"),
            model_settings=ModelSettings(temperature=0.7),
            tools=[],
        )

    def get(self, name: str) -> Agent:
        try:
            return self._agents[name]
        except KeyError:
            raise ValueError(f"Unknown agent: {name}")

    async def run_agent(self, name: str, input: str) -> str:
        agent = self.get(name)
        run_result = await Runner.run(agent, input=input)
        return run_result.final_output
