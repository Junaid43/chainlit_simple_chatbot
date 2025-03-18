from agents.tool import function_tool
import chainlit as cl

@function_tool("get_weather")
@cl.step(type="weather_tool")
def get_weather(location: str, unit: str = "C") -> str:
  """
  Fetch the weather for a given location, returning a short description.
  """
  # Example logic
  return f"The weather in {location} is 32 degrees {unit}."

@function_tool("piaic_student_finder")
def student_finder(student_roll: int) -> str:
  """
  find the PIAIC student based on the roll number
  """
  data = {1: "Qasim",
          2: "Sir Zia",
          3: "Daniyal"}

  return data.get(student_roll, "Not Found")