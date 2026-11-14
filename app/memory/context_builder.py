class MemoryContextBuilder:

    def build(
        self,
        conversation_messages: list[dict],
        long_term_memories: list[dict],
    ) -> list[dict]:

        memory_text = "\n".join(
            f"- [{memory['category']}] {memory['content']}"
            for memory in long_term_memories
        )

        system_context = (
            "You are Jarvis, a personal AI assistant.\n\n"
            "Relevant information about the user:\n"
            f"{memory_text or 'No stored memories available.'}\n\n"
            "Use these memories only when relevant. "
            "Do not assume information that is not present."
        )

        return [
            {"role": "system", "content": system_context},
            *conversation_messages,
        ]