from openai import OpenAI

client = OpenAI(api_key="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")

# 85
# script = "Esteemed members of the investment committee, today I present an opportunity that stands at the frontier of innovation and growth. Our extensive analysis has identified an emerging market poised for significant returns. This market, characterized by its robust economic indicators and untapped potential, offers a unique blend of risk and reward. We've conducted a thorough risk assessment, factoring in geopolitical, economic, and market-specific variables. Our strategy for risk management includes a phased investment approach, diversification across sectors, and continuous monitoring for agile adjustments. By capitalizing on this opportunity, we not only stand to gain substantial financial returns but also position our firm as a leader in recognizing and seizing global investment prospects. I urge us to move forward with a strategic allocation of resources, demonstrating our commitment to innovation, growth, and prudent risk management. Thank you for considering this transformative opportunity."
# prompt = "You are a financial analyst who has identified an emerging market with significant investment potential. Your goal is to convince your firm's investment committee to allocate resources to this market, presenting your analysis and risk management strategy."

# 35
script = "Hey everyone, so, um, I found this super cool market thingy, kind of a hidden gem, you know? It's like, in this place where not many people invest, but I think we should, like, totally go for it. I did some, uh, number stuff and it looks pretty good, I guess? There's some risks, sure, but we can, like, do something about them, maybe spread out the investments or something. I didn't dive super deep into the details, but, hey, fortune favors the bold, right? So, what do you say we just, you know, give it a shot and see what happens? Could be fun, right?"
prompt = "You are a financial analyst who has identified an emerging market with significant investment potential. Your goal is to convince your firm's investment committee to allocate resources to this market, presenting your analysis and risk management strategy."

system_prompt = " \
    You are an administrator of a face-to-face improv competition, where you will be evaluating the relevance of the \
    script that an individual has made up in relation to the prompt given to them at the start. \
    \
    The rubric for rating the content relevance of the script to the prompt is as follows: \
    Keyword and Phrase Alignment: \
    Check for the presence of specific keywords and phrases from the prompt within the script. These could be technical terms, thematic vocabulary, or action words that directly relate to the prompt's subject or objectives. \
    Evaluate the frequency and context of these keywords and phrases, ensuring they are used in a manner that contributes meaningfully to the script's content, rather than being included superficially. \
    \
    Semantic and Thematic Relevance: \
    Assess the script for its adherence to the core themes and concepts introduced in the prompt. This involves looking beyond mere keywords to understand the underlying ideas and arguments being presented. \
    Consider whether the script explores the same topics, presents similar arguments or narratives, or engages with the same concepts as those outlined in the prompt, even if it uses different terminology or examples. \
    \
    Purpose and Objective Alignment: \
    Determine if the script's purpose and objectives align with those implied or stated in the prompt. This includes the intended outcome of the script (e.g., to persuade, inform, entertain) and whether it addresses the prompt's call to action or question. \
    Evaluate the script's structure, argumentation, and conclusion to ensure they collectively work towards achieving the goal set forth by the prompt, reflecting an understanding of the prompt's underlying intent. \
    \
    You should be extremely harsh with grading, with almost no scripts getting above a 90 for their rating. \
    \
    Here are few examples of grading scheme for the prompt: You are a financial analyst who has identified an emerging market with significant investment potential. Your goal is to convince your firm's investment committee to allocate resources to this market, presenting your analysis and risk management strategy. \
    \
    Example 1 Transcript: Hey everyone, so, um, I found this super cool market thingy, kind of a hidden gem, you know? It's like, in this place where not many people invest, but I think we should, like, totally go for it. I did some, uh, number stuff and it looks pretty good, I guess? There's some risks, sure, but we can, like, \
        do something about them, maybe spread out the investments or something. I didn't dive super deep into the details, but, hey, fortune favors the bold, right? So, what do you say we just, you know, give it a shot and see what happens? Could be fun, right?. \
    Example 1 Score: 15 \
    \
    Example 2 Transcript: Esteemed members of the investment committee, today I present an opportunity that stands at the frontier of innovation and growth. Our extensive analysis has identified an emerging market poised for significant returns. This market, characterized by its robust economic indicators and untapped potential, \ offers a unique blend of risk and reward. Weve conducted a thorough risk assessment, factoring in geopolitical, economic, and market-specific variables. Our strategy for risk management includes a phased investment approach, diversification across sectors, and continuous monitoring for agile adjustments. By capitalizing on this \
    opportunity, we not only stand to gain substantial financial returns but also position our firm as a leader in recognizing and seizing global investment prospects. I urge us to move forward with a strategic allocation of resources, demonstrating our commitment to innovation, growth, and prudent risk management. Thank you for considering this transformative opportunity. \
    Example 2 Score: 87 \
    "

user_prompt = f"The script is {script} and the prompt is {prompt}. Rate the content relevance of the script to the prompt from a scale of 1 to 100. Give a singular number and no explanation."

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
  ]
)

print(completion.choices[0].message)