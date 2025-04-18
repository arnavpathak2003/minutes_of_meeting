from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from .tools.email_tool import EmailTool
from dotenv import load_dotenv
load_dotenv()


@CrewBase
class SendEmail:
    """SendEmail crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def gmail_draft_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["gmail_draft_agent"],
            verbose=True,
            # llm=self.llm,
            tools=[EmailTool()],
        )

    @task
    def gmail_send_task(self) -> Task:
        return Task(
            config=self.tasks_config["gmail_send_task"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SendEmail crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
