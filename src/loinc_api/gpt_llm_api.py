from openai import OpenAI

client = OpenAI(api_key="")

resp = client.responses.create(
    model="gpt-4.1-mini",
    input="Explain quantum computing in simple terms."
)

print(resp.output[0].content[0].text)
