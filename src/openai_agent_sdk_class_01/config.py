import asyncio
# from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled,AsyncOpenAI,RunConfig
from dotenv import load_dotenv, find_dotenv
import os

_:bool = load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY")


# #Reference: https://ai.google.dev/gemini-api/docs/openai


# Step 1 Provider
client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

# Step 2 Model
model = OpenAIChatCompletionsModel(
        model='gemini-2.0-flash',
        openai_client=client
    )

model2 = OpenAIChatCompletionsModel(
        model='gemini-1.5-flash',
        openai_client=client
    )

# Step 3 Run

run_config = RunConfig(
        model=model,
        model_provider=client,
        tracing_disabled=True
    )

run_config_gemini_1_5_flash = RunConfig(
        model=model2,
        model_provider=client,
        tracing_disabled=True
    )

chatbot_agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant",
    )