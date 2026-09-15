---
id: software/system-design/book-60-days/day-46-enforcing-structured-output-from-an-llm
canonical_question: Enforcing Structured Output from an LLM
aliases:
- System Design Day 46
- Enforcing Structured Output from an LLM
- Day 46 scenario
entity_type: book_chapter
domain: software > system-design > workbook
last_verified: 2026-08-18
---

# Day 46: Enforcing Structured Output from an LLM

DAY 46 · SYSTEM DESIGN
Enforcing Structured Output from an LLM
Your production LLM agent just returned this JSON to your order processing service:
{
"action": "refund",
"amount": "fifty dollars",
"order_id": null,
"confidence": "pretty high"
}
Your downstream service crashes. The retry hits the same model. Same broken output. The refund never
fires — but the user got a confirmation email.
You need your agent to return valid, typed, structured output — every time. What do you do?

---

DAY 46 · ANSWERS & EXPLANATIONS
Answer 1 ✓  CORRECT ANSWER
Why B wins (Structured outputs / API-level schema enforcement):
This is the only option that eliminates the problem at the source. When you use OpenAI's
response_format: { type: "json_schema" }, Bedrock's tool use / converse API, or Gemini's
response_schema, the model's token sampling is constrained — it cannot produce output that violates
the schema. Not "it's less likely." Cannot.
Under the hood, these APIs use constrained decoding: the model's output probability distribution is
masked so invalid tokens are zeroed out at each step. The result is guaranteed schema conformance
on every call. No retries. No parsing. No "it worked 98% of the time."
In production: use Pydantic (Python) or Zod (TypeScript) to define your schema, pass it to the API,
deserialize directly into your typed model. Your downstream service never sees a string where it
expects an int.
