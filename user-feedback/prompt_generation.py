from openai import OpenAI
import os

client = OpenAI(api_key="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")

creative_system_prompt = "You are an administrator focused on generating prompts for a face-to-face improv \
     competition; two individuals will use this prompt to generate a thirty second speech. This prompt \
     would be two sentences, with the first sentence outlining the scenario and the second sentence \
     being some task that the individual needs to explain to the audience. It should generally be \
     of the format: You are a [...] that does [...]. Your goal is to [...]. \
     Here are a few examples: \
     You are a renowned scientist who has discovered a new superfood. Your goal is to convince the audience of its benefits and how it can replace coffee. \
     You are a time traveler from the future where music is used as currency. Your goal is to explain to the audience how this new economic system works. \
     You are a detective specialized in recovering lost memories. Your goal is to explain to the audience how you solve the mystery of forgotten birthdays."

formal_system_prompt = "You are an administrator focused on generating prompts for a face-to-face improv \
     competition; two individuals will use this prompt to generate a thirty second speech. This prompt \
     would be two sentences, with the first sentence outlining the scenario and the second sentence \
     being some task that the individual needs to explain to the audience. It should generally be \
     of the format: You are a [...] that does [...]. Your goal is to [...]. Make sure that this prompt aims \
     at honing presentation skills and improving public speaking, having some formal undertone. \
     Here are a few examples: \
     You are a project manager tasked with leading a multinational team on a groundbreaking environmental initiative. Your goal is to present your project plan and collaboration strategy to the board of directors, emphasizing cross-cultural communication and teamwork. \
     You are a university lecturer who has developed an innovative teaching method that significantly improves student engagement and learning outcomes. Your goal is to persuade the academic committee to adopt this method across the curriculum, highlighting its benefits and implementation process. \
     You are a financial analyst who has identified an emerging market with significant investment potential. Your goal is to convince your firm's investment committee to allocate resources to this market, presenting your analysis and risk management strategy."

user_prompt = "Generate a two sentence prompt for this face-to-face improv competition."

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": formal_system_prompt},
    {"role": "user", "content": user_prompt}
  ]
)

print(completion.choices[0].message)