import chainlit as cl
import subprocess
from chainlit.types import ThreadDict
from openai_agent_sdk_class_01.config import chatbot_agent,run_config,run_config_gemini_1_5_flash
from openai.types.responses import ResponseTextDeltaEvent
from agents import Runner
from typing import Optional
from chainlit.input_widget import Select, Switch, Slider,TextInput

from openai_agent_sdk_class_01.tools.tool import get_weather

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="gemini-1.5-flash",
            markdown_description="The underlying LLM model is **Gemini 1.5 Flash**.",
            icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="gemini-2.0-flash",
            markdown_description="The underlying LLM model is **Gemini 2.0 Flash**.",
            icon="https://picsum.photos/250",
        ),
    ]

@cl.on_chat_start
async def on_chat_start():
    chat_profile = cl.user_session.get("chat_profile")
    cl.user_session.set("history", [])
    cl.user_session.set("history_gemini_1_5", [])
   
    elements = [
        cl.File(
            name="My CV",
            path="./cv.pdf",
            display="inline",
            page=1
        ),
    ]

    if chat_profile == "gemini-2.0-flash":
       await cl.Message(
        content=f"Hello! I am a {chat_profile} chatbot. I can help you with anything you want to talk about Its a reasoning model . Here's my profile", elements=elements,
        ).send()
    else:
        None
        
  

@cl.set_starters
async def set_starters():
    
    return [
        cl.Starter(
            label="Weather",
            message="Find the weather of cities in Lahore, Pakistan",
        ),
        cl.Starter(
            label="Python Coding",
            message="Basics of Python",
        )

    ]


@cl.on_message
async def main(message: cl.Message):
    history= cl.user_session.get("history")
    history_gemini_1_5 = cl.user_session.get("history_gemini_1_5")
    chat_profile = cl.user_session.get("chat_profile")

    if chat_profile == "gemini-1.5-flash":
        # Create a new message object for streaming
        msg2 = cl.Message(content="")
        await msg2.send()
         # Create a new message object for streaming
        print(f"chat profile is gemini 1.5 flash {chat_profile}")
        history_gemini_1_5.append({"role":"user", "content":message.content})
        result2 = Runner.run_streamed(
            run_config=run_config_gemini_1_5_flash,
            input=history_gemini_1_5,
            starting_agent=chatbot_agent
        )
        print(f"result2 {result2}")
        
        history_gemini_1_5.append({"role":"assistant", "content":result2.final_output})
        cl.user_session.set("history_gemini_1_5", history_gemini_1_5)
        async for event in result2.stream_events():
            if event.type=='raw_response_event' and isinstance(event.data, ResponseTextDeltaEvent):
                await msg2.stream_token(event.data.delta)
        await cl.Message(content=result2.final_output).update()
    else:
        msg = cl.Message(content="")
        await msg.send()
        print(f"chat profile is gemini 2.0 flash {chat_profile}")
        history.append({"role":"user", "content":message.content})
        result = Runner.run_streamed(
            run_config=run_config,
            input=history,
            starting_agent=chatbot_agent
        )
        history.append({"role":"assistant", "content":result.final_output})
        cl.user_session.set("history", history)
        async for event in result.stream_events():
            if event.type=='raw_response_event' and isinstance(event.data, ResponseTextDeltaEvent):
                await msg.stream_token(event.data.delta)
        await cl.Message(content=result.final_output).update()

    # result = await Runner.run(
    #     run_config=run_config,
    #     input=history,
    #     starting_agent=chatbot_agent
    # )


    # To use a tool and fetching from the function tools
    # chatbot_agent.tools.append(get_weather)

    # Send a response back to the user
    # await cl.Message(
    #     content=f"Received: {result.final_output}",
    # ).send()

  


@cl.on_chat_resume
async def on_chat_resume(thread:ThreadDict):
    history = cl.user_session.get("history")
    chat_profile = cl.user_session.get("chat_profile")
    history_gemini_1_5 = cl.user_session.get("history_gemini_1_5")

    
    cl.user_session.set("history", [])
    cl.user_session.set("history_gemini_1_5", [])

    if history and chat_profile == "gemini-2.0-flash":
       # send the context to user
        # for chat in history:
        #     role = chat['role']
        #     content = chat['content']
        #     if role == 'user':
        #        await cl.Message(content=content, author="User").send()
        #     else:
        #        await cl.Message(content=content, author="Assistant").send()

        for message in thread["steps"]:
            if message["type"] == "user_message":
                history.append({"role": "user", "content": message["output"]})
            elif message["type"] == "assistant_message":
                history.append({"role": "assistant", "content": message["output"]})
    elif history_gemini_1_5 and chat_profile == "gemini-1.5-flash":
        # for chat in history_gemini_1_5:
        #     role = chat['role']
        #     content = chat['content']
        #     if role == 'user':
        #        await cl.Message(content=content, author="User").send()
        #     else:
        #        await cl.Message(content=content, author="Assistant").send()

        for message in thread["steps"]:
            if message["type"] == "user_message":
                history_gemini_1_5.append({"role": "user", "content": message["output"]})
            elif message["type"] == "assistant_message":
                history_gemini_1_5.append({"role": "assistant", "content": message["output"]})
    else:
        await cl.Message(content="No previous chat history found. Starting a new conversation.").send()

@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")

def run_chainlit():
    subprocess.run(['chainlit', 'run', 'src/openai_agent_sdk_class_01/chatbot.py', '-w'])