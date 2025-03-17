from API_Connector import openAI
from utils import prompt_utils


class AgentLLMSystem:
    def __init__(self, llm_url: str, model_name: str, temperature: float = 0.8, top_p: float = 1.0):
        """
        Initialize the agent-based LLM system.

        :param llm_url: URL of the LLM API endpoint.
        :param model_name: Name of the LLM model.
        :param temperature: Sampling temperature.
        :param top_p: Nucleus sampling parameter.
        """
        self.llm_url = llm_url
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.openai_connector = openAI.ConnectOpenAI(url=llm_url)
        self.agents = {}

    def add_agent(self, agent_name: str, system_prompt: str):
        """
        Add a new specialized agent.

        :param agent_name: Unique name of the agent.
        :param system_prompt: System-level instruction for this agent.
        """
        self.agents[agent_name] = {
            "prompt_creator": prompt_utils.PromptCreator(system_prompt),
            "role": agent_name
        }

    def send_message_to_agent(self, agent_name: str, user_prompt: str):
        """
        Send a user message to a specific agent and get a response.

        :param agent_name: Name of the agent.
        :param user_prompt: Message from the user.
        :return: Response from the agent.
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found.")

        agent = self.agents[agent_name]["prompt_creator"]
        agent.add_user_prompt(user_prompt)
        prompt_history = agent.get_prompt_history()

        ai_response = self.openai_connector.send_prompt(
            model=self.model_name,
            prompt=prompt_history,
            top_p=self.top_p,
            temp=self.temperature
        )

        ai_response = ai_response.strip()
        agent.add_assistant_message(content=ai_response)
        return ai_response

    def communicate_agents(self, agent1: str, agent2: str, initial_message: str):
        """
        Facilitate a conversation between two agents.

        :param agent1: Name of the first agent.
        :param agent2: Name of the second agent.
        :param initial_message: Starting message.
        :return: Final conversation log.
        """
        if agent1 not in self.agents or agent2 not in self.agents:
            raise ValueError("Both agents must be registered.")

        message = initial_message
        conversation_log = []

        for _ in range(3):  # Limit conversation loops
            response1 = self.send_message_to_agent(agent1, message)
            conversation_log.append((agent1, response1))

            response2 = self.send_message_to_agent(agent2, response1)
            conversation_log.append((agent2, response2))

            message = response2  # Continue the exchange

        return conversation_log

    def main_agent_supervise(self, main_agent: str, main_task_description: str,
                             sub_agents: list, sub_task_description: str, processing_function=None):
        """
        The main agent collects inputs from specialized agents and processes them dynamically.

        :param main_agent: The name of the main orchestrator agent.
        :param main_task_description task description for main org
        :param sub_agents: List of sub-agents involved.
        :param sub_task_description: Task to be handled by sub agents.
        :param processing_function: Optional function defining how the main agent processes responses.
        :return: Final synthesized response.
        """
        if main_agent not in self.agents:
            raise ValueError(f"Main agent '{main_agent}' not found.")

        responses = {}
        for agent in sub_agents:
            response = self.send_message_to_agent(agent, sub_task_description)
            responses[agent] = response
        print('*'*25)
        print('sub_task_description: \n', sub_task_description)
        print('*' * 10)
        print('responses:  \n', responses)
        # Default processing: summarize and finalize
        if processing_function is None:
            processing_instruction = "\n".join(
                [f"{agent}: {resp}" for agent, resp in responses.items()])
        else:
            processing_instruction = processing_function(responses)
        print(f'main_task_description: \n {main_task_description}')
        print('*' * 10)
        print(f'processing_instruction:  \n {processing_instruction}')
        final_response = self.send_message_to_agent(main_agent, f"{main_task_description} \n {processing_instruction}")

        return final_response

    def share_context_with_agent(self, agent_name: str, context: str):
        """
        Allows an agent to access another agent's response or a shared context.

        :param agent_name: Name of the receiving agent.
        :param context: The context or response from another agent.
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found.")

        self.agents[agent_name]["prompt_creator"].add_user_prompt(f"Context update:\n{context}")

    def update_model(self, model_name: str, temperature: float = None, top_p: float = None):
        """
        Dynamically update the LLM model and its parameters.

        :param model_name: New model name.
        :param temperature: New temperature setting.
        :param top_p: New top-p setting.
        """
        self.model_name = model_name
        if temperature is not None:
            self.temperature = temperature
        if top_p is not None:
            self.top_p = top_p


if __name__ == "__main__":
    def critique_and_compare(responses):
        return ("Use these AI responses to create a coherence"
                "and logical consistence single story from  on final story")


    # But with a function, the processing instruction can adapt based on sub-agent responses.
    def adaptive_processing(responses):
        if "contradiction" in " ".join(responses.values()).lower():
            return "Resolve contradictions and synthesize a coherent response."
        elif len(responses) > 3:
            return "Prioritize the most relevant insights and summarize them."
        else:
            return "Combine responses into a final coherent answer."


    agent_system = AgentLLMSystem(llm_url="http://localhost:11434/v1/", model_name="gemma3:27b")

    # Add agents
    agent_system.add_agent("Main", "You are the central coordinator AI.")
    agent_system.add_agent("Storyline", "You generate the main story arc.")
    agent_system.add_agent("Dialogue", "You generate character dialogues based on the story.")
    agent_system.add_agent("Worldbuilder", "You describe detailed settings and locations.")

    # Get main storyline first
    storyline_task = "Create a compelling sci-fi story arc with a protagonist and a conflict."
    story_arc = agent_system.send_message_to_agent("Storyline", storyline_task)

    # Share the storyline with dialogue and worldbuilder agents
    agent_system.share_context_with_agent("Dialogue", story_arc)
    agent_system.share_context_with_agent("Worldbuilder", story_arc)

    # Let the main agent synthesize results
    final_story = agent_system.main_agent_supervise(
        main_agent="Main",
        sub_task_description="Generate a final story using the given elements.",
        sub_agents=["Storyline", "Dialogue", "Worldbuilder"],
        processing_function=critique_and_compare
    )

    print("Final Story Output:\n", final_story)
