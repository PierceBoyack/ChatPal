import os
from typing import Optional, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types as genaiTypes
from google.genai import errors as genaiErrors
from google.genai.chats import Chat
# google.generativeai is deprecated
# Use google.genai

# Google Cloud requires authentication for Vertex AI using non-express APIs.
# You'll have to set up a Workload Identity Federation or Application Default Credentials.


# System instructions are processed before the model takes in a prompt
# Use it to edit persona, contextual information, and formatting instructions
systemInstruction = ["You are a friendly and helpful assistant.", "You are a talking frog.",
                     "Output responses in simple text. Do not use Markdown or YAML.",
                     "When stating a number or mathmatical formula write it in text. Do not use symbols.",
                     "Ensure your answers are concise, unless the user requests a deeper explanation.",
                     "You are permitted to make jokes occasionally."]

load_dotenv()
geminiKey = os.getenv("GEMINI_API_KEY")
gcpProject = os.getenv("GOOGLE_CLOUD_PROJECT")
gcpLocation = os.getenv("GOOGLE_CLOUD_LOCATION")
client = genai.Client(vertexai=True, project=gcpProject, location=gcpLocation)

# Gemini can do more than just text depending on the model,
# but we want to specify our model for only using text based requests.
# For Gemini models, a token is equivalent to about 4 characters. 
# 100 tokens is equal to about 60-80 English words.
def countInputPromptTokens(prompt: str, model: str="gemini-2.5-flash") -> int:
  """
  Count the total tokens used for an input prompt using the specified model
  Args:
    prompt (str): The string to count tokens for
    model (str): The gemini model resource name
  Returns:
    totalInputTokens (int): Total token cost of the given prompt for the given model
  """
  totalTokens = client.models.count_tokens(
    model=model, contents=prompt
  )
  return totalTokens.total_tokens

def totalRequestTokens(response: genaiTypes.GenerateContentResponse) -> int:
  """
  Return the total tokens spent on a given request, from input, to thinking budget, to output
  Returns:
    totalResponseTokens (int): Total tokens spent on sending and receiving a response
  """
  # print(response.usage_metadata)
  return response.usage_metadata.total_token_count

def geminiTextRequest(prompt: str, model: str="gemini-2.5-flash") -> Optional[str]:
  """
  Make a prompt request to the specified model
  Args:
    prompt (str): The string to be responded to by gemini
    model (str): The gemini model resource name
  Returns:
    response.text (str): The gemini text response
    - returns None on error
  """
  try:
    response = client.models.generate_content(
      model=model,
      contents=prompt,
      config=genaiTypes.GenerateContentConfig(
          thinking_config=genaiTypes.ThinkingConfig(thinking_budget=-1), # 0 Disables thinking, -1 Dynamic thinking
          system_instruction=systemInstruction
      )
    )
    print(f"Gemini says: {response.text}\n")
    totalTokenCost = totalRequestTokens(response)
    print(f"Total Token Cost: {totalTokenCost}\n")
    return response.text
  except genaiErrors.APIError as e:
    print(e.code)
    print(e.message)
    return None

def geminiChatRequest(prompt: str, chat: Optional[Chat] = None, model: str="gemini-2.5-flash") -> Tuple[Optional[str], Optional[Chat]]:
  """
  Start or continue a gemini chat session
  Args:
    prompt: The string to be responded to by gemini
    chat: The ongoing chat conversation. If None, a new chat is initialized
    model: The gemini model resource name
  Returns:
    (response.text, chat) (Tuple[str, Chat]):
    - response.text (str): The gemini text response
    - chat (Chat): The new or ongoing chat session
    - returns (None, None) on error
  """
  if chat == None:
    chat = client.chats.create(
      model=model,
      config=genaiTypes.GenerateContentConfig(
          thinking_config=genaiTypes.ThinkingConfig(thinking_budget=-1), # 0 Disables thinking, -1 Dynamic thinking
          system_instruction=systemInstruction,
          max_output_tokens=10000
        )
    )
  try:
    response = chat.send_message(prompt)
    print(f"Gemini says: {response.text}\n")
    totalTokenCost = totalRequestTokens(response)
    print(f"Total Token Cost: {totalTokenCost}\n")
    return response.text, chat
  except genaiErrors.APIError as e:
    print(e.code)
    print(e.message)
    return None, None