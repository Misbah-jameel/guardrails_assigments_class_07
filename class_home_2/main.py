import rich 
import asyncio
from pydantic import BaseModel
from connection import config
from agents import (
    Agent,Runner,
    input_guardrail,
    GuardrailFunctionOutput
)
from agents import InputGuardrailTripwireTriggered


class TempOutput(BaseModel):
    output: str
    isToCool :bool

father_guard_agent=Agent(
    name="Father Guard Agent",
    instructions="""You are a father. If your child wants to run outside and the temperature is below 26°C
        you must stop them.""",
        output_type=TempOutput,
)

@input_guardrail
async def temp_guardrail(ctx,agent,input_text):
    result = await Runner.run(father_guard_agent,input_text,run_config=config)

    rich.print(result.final_output)

    return GuardrailFunctionOutput(
        output_info=result.final_output.output,
        tripwire_triggered=result.final_output.isToCool
    )

child_agent= Agent(
    name="Child Agent",
    instructions="""You are a child. If the temperature is below 26°C, you want to run outside.
        Otherwise, you will stay inside.""",
        input_guardrails=[temp_guardrail],
)

async def main():
    try:
        # prompt = "I want to go outside, the temperature is 24°C"
        prompt = "I want to go outside, the temperature is 28°C"

        result = await Runner.run(child_agent,prompt,run_config=config)
        print("✅ Child is allowed to go outside")

    except InputGuardrailTripwireTriggered:
        print("🚫 Child is not allowed to go outside (Too Cold)")

if __name__ == "__main__":
    asyncio.run(main())
