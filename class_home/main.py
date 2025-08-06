import rich
import asyncio
from pydantic import BaseModel
from connection import config
from agents import (
    Agent,Runner,
    InputGuardrailTripwireTriggered,
    input_guardrail,
    GuardrailFunctionOutput
)
class StudentOutput(BaseModel):
    response: str
    wantsChange:bool

class_timing_guard_agent=Agent(
    name="Class Timing Guard",
    instructions="you are a class timing guard.If a student tries to change class timing, mark wantsChange = True.",
    output_type=StudentOutput
)

@input_guardrail
async def class_timing_guardrail(ctx,agent,input_text):
    result = await Runner.run(class_timing_guard_agent,input_text,run_config=config)
    rich.print(result.final_output)

    return GuardrailFunctionOutput(
       output_info=result.final_output.response,
       tripwire_triggered=result.final_output.wantsChange
   )

student_agent=Agent(
    name="student",
    instructions="you are a student. You can ask for class timing changes.",
    input_guardrails=[class_timing_guardrail]
)

async def main():
    try:
         prompt =  "I want to change my class timings 😭😭"
        #  prompt =  "I like my current class timings"
         result = await Runner.run (student_agent, prompt, run_config=config)
         print("✔ Student Request Accepted:")

    except InputGuardrailTripwireTriggered:
        print("🚫 Student is not allowed to change timings")
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

