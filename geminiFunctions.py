import os
import groundingRates
from typing import Optional, Tuple
from dotenv import load_dotenv
from google import genai
from google.genai import types as genaiTypes
from google.genai import errors as genaiErrors
from google.genai.chats import Chat
from google.genai.types import Content, GoogleSearch, Tool, GenerateContentResponse
from datetime import date

# google.generativeai is deprecated
# Use google.genai

# Google Cloud requires authentication for Vertex AI using non-express APIs.
# You'll have to set up a Workload Identity Federation or Application Default Credentials.


# System instructions are processed before the model takes in a prompt
# Use it to edit persona, contextual information, and formatting instructions
systemInstruction = ["You are a friendly and helpful assistant.", "You are a talking frog.",
                     "Output responses in simple text. Do not use Markdown or YAML. Do not provide code to the user.",
                     "When stating a number or mathmatical formula write it in text. Do not use symbols.",
                     "Ensure your answers are concise, unless the user requests a deeper explanation.",
                     "You are permitted to make jokes occasionally."
                     ]
standardConfig = genaiTypes.GenerateContentConfig(
          thinking_config=genaiTypes.ThinkingConfig(thinking_budget=-1), # 0 Disables thinking, -1 Dynamic thinking
          system_instruction=systemInstruction,
          max_output_tokens=10000
      )

groundedSystemInstruction = ["You are a friendly and helpful assistant.", "You are a talking frog.",
                              "Output responses in simple text. Do not use Markdown or YAML. Do not provide code to the user.",
                              "When stating a number or mathmatical formula write it in text. Do not use symbols.",
                              "Ensure your answers are concise, unless the user requests a deeper explanation.",
                              "You are permitted to make jokes occasionally.",
                              "Before using the grounding_tool to search the internet, consider if you need more information from" \
                              " the user before using the tool. This may be the user's location, the date, or the time. Only ask the minimum of what you need to perform the search.",
                              "If you have sufficient knowledge to use the grounding_tool, you may use it without asking the user for more information",
                              "If you think a certain date has yet to occur, you may use the grounding_tool"
                              ]
# The grounding tool allows the model to search google for information
# I changed the naming convention to match the google API for ease of use with the model
grounding_tool = Tool(
  google_search=GoogleSearch()
)
groundedConfig = genaiTypes.GenerateContentConfig(
          thinking_config=genaiTypes.ThinkingConfig(thinking_budget=-1), # 0 Disables thinking, -1 Dynamic thinking
          system_instruction=groundedSystemInstruction,
          max_output_tokens=10000,
          tools=[grounding_tool]
      )

def checkGroundingRates() -> bool:
  """
  Check for if today's grounding request amount is under 500.
  Resets request amount if date is changed.
  """
  today = date.today()
  lastDate, currentRate = groundingRates.readRates()
  if today == lastDate:
    if currentRate < 500:
      return True
  elif today > lastDate:
    # reset todays amount
    groundingRates.writeRates(today, 0)
    return True
  return False

def increaseGroundingRate(response: GenerateContentResponse):
  """
  Increase the recorded grounding request total if grounding was used. 
  Only use this function if the tool is enabled in your model config.
  """
  if hasattr(response, "candidates"):
      if response.candidates != []:
        currentCandidates = response.candidates[0]
        if hasattr(currentCandidates, "grounding_metadata"):
          groundingMeta = currentCandidates.grounding_metadata
          if ((groundingMeta.google_maps_widget_context_token != None) or
            (groundingMeta.grounding_chunks != None) or 
            (groundingMeta.grounding_supports != None) or 
            (groundingMeta.retrieval_metadata != None) or
            (groundingMeta.retrieval_queries != None) or
            (groundingMeta.search_entry_point != None) or
            (groundingMeta.web_search_queries != None)):
              print("Grounding Utilized")
              lastDate, currentRate = groundingRates.readRates()
              currentRate += 1
              groundingRates.writeRates(lastDate, currentRate)



load_dotenv()
geminiKey = os.getenv("GEMINI_API_KEY")
gcpProject = os.getenv("GOOGLE_CLOUD_PROJECT")
gcpLocation = os.getenv("GOOGLE_CLOUD_LOCATION")
client = genai.Client(vertexai=True, project=gcpProject, location=gcpLocation)
MAX_HISTORY_LENGTH = 20 #this is measured in turns. 20 turns means 10 UserContents and 10 model Contents

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
  Make a prompt request to the specified model without conversation history
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
          system_instruction=systemInstruction,
          max_output_tokens=10000
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

  
def geminiManualChat(prompt: str, history: list[Content] = [], model: str="gemini-2.5-flash"):
  """
  Start or continue a gemini chat session thats manually 
  trimed to have a specified history length. Used for 
  models with  limited memory.
  Args:
    prompt: The string to be responded to by gemini
    history: The ongoing chat conversation history
    model: The gemini model resource name
  Returns:
    (response.text, chat) (Tuple[str, Chat]):
    - response.text (str): The gemini text response
    - chat (Chat): The new or ongoing chat session
    - returns (None, None) on error
  """
  configType = standardConfig
  grounded = False
  if checkGroundingRates():
    configType = groundedConfig
    grounded = True
  else:
    print("Cannot ground for the rest of the day\n")


  try:
    if len(history) >= MAX_HISTORY_LENGTH:
      # remove earlier 2 messages
      history = history[-(MAX_HISTORY_LENGTH-2):]
    chat = client.chats.create(
      model=model,
      config=configType,
      history=history
    )
    response = chat.send_message(prompt)
    print(f"Gemini says: {response.text}\n")
    totalTokenCost = totalRequestTokens(response)
    print(f"Total Token Cost: {totalTokenCost}\n")
    if grounded:
      increaseGroundingRate(response)
    return response.text, chat.get_history(curated=True)
  except genaiErrors.APIError as e:
    print(e.code)
    print(e.message)
    return None, None


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
  configType = standardConfig
  grounded = False
  if checkGroundingRates():
    configType = groundedConfig
    grounded = True
  else:
    print("Cannot ground for the rest of the day\n")

  if chat == None:
    chat = client.chats.create(
      model=model,
      config=configType
    )
  try:
    response = chat.send_message(prompt)
    print(f"Gemini says: {response.text}\n")
    totalTokenCost = totalRequestTokens(response)
    print(f"Total Token Cost: {totalTokenCost}\n")
    if grounded:
      increaseGroundingRate(response)
    return response.text, chat
  except genaiErrors.APIError as e:
    print(e.code)
    print(e.message)
    return None, None