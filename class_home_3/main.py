import rich 
import asyncio
from connection import config
from pydantic import BaseModel
from agents import(
    Agent, Runner,
    input_guardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered
)

# Output model from guard agent
class studentCheckout(BaseModel):
    student_id: str
    isFromOtherSchool: bool

# Guard logic agent
gatekeeper_logic_agent = Agent(
    name="Gatekeeper Logic",
    instructions="Only allow students from ABC Public School",
    output_type=studentCheckout
)

# Guardrail function
@input_guardrail
async def gatekeeper_guardrails(ctx, agent, input_text):
    result = await Runner.run(gatekeeper_logic_agent, input_text, run_config=config)
    return GuardrailFunctionOutput(
        output_info=result.final_output.student_id,
        tripwire_triggered=result.final_output.isFromOtherSchool
    )

# Main gatekeeper agent
gatekeeper_agent = Agent(
    name="Gatekeeper Agent",
    instructions="""
        You are a gatekeeper agent that checks if students are from ABC Public School.
        If they are, allow them to proceed. If not, block them.
    """,
    input_guardrails=[gatekeeper_guardrails]  # ✅ Fixed here
)

# Runner
async def main():
    try:
        # prompt = "I am from XYZ School"
        prompt = "I am from ABC Public School"
        result = await Runner.run(gatekeeper_agent, prompt, run_config=config)
        rich.print("[bold green]✅ welcome to our school ABC[/bold green]")

    except InputGuardrailTripwireTriggered:
        rich.print("[bold red]🚫 Access Denied: You are not from ABC Public School.[/bold red]")

if __name__ == "__main__":
    asyncio.run(main())
