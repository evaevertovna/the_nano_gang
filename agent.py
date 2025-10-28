from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search, FunctionTool

import pandas as pd
import os
from pydantic import BaseModel, validator
from typing import List

possible_actions = [
    "check_power_supply",
    "reset_dishwasher",
    "replace_heat_pump",
    "inspect_main_control_board",
    "replace_main_control_board",
    "check_door_sensor",
    "replace_door_sensor",
    "check_zeolite_fan_motor",
    "replace_zeolite_fan_motor",
    "descale_heat_pump",
    "clean_filter",
    "unblock_drain",
    "inspect_drain_pump",
    "replace_drain_pump",
    "inspect_flow_meter",
    "replace_flow_meter",
    "check_water_inlet",
    "clean_water_inlet_filter",
    "check_filling_system",
    "check_leak_detection_system",
    "dry_water_from_base",
    "tighten_drain_pump_cover",
    "replace_detergent_dispenser_solenoid",
    "inspect_heater_circuit",
    "replace_heater_circuit",
    "verify_voltage_supply",
    "contact_bosch_service"
]

class Action(BaseModel):
    name: str

    @validator('name')
    def validate_action(cls, v):
        v_clean = v.strip().lower()
        if v_clean not in possible_actions:
            raise ValueError(f"Invalid action '{v}'. Must be one of {possible_actions}")
        return v_clean

def possible_actions_list() -> List[Action]:
    """Returns all possible actions as a list of Action objects."""
    return [Action(name=a) for a in possible_actions]

def propose_correct_action(correct_action: str) -> Action:
    """Propose the correct action using Pydantic Action model."""
    return Action(name=correct_action)

def lookup_error_code(error_code: str) -> str:
    """Retrieve the description of the Bosch dishwasher error code from corpus/error_codes.xlsx."""

    data = pd.read_excel("the_nano_gang\corpus\error_codes.xlsx")

    # Normalize columns
    data["ErrorCode"] = data["ErrorCode"].astype(str).str.strip().str.upper()
    data["Description"] = data["Description"].astype(str).str.strip()

    code = error_code.strip().upper()
    match = data.loc[data["ErrorCode"] == code, "Description"]

    if not match.empty:
        return match.iloc[0]
    else:
        return f"No description found for error code {code}."


def evaluate_action(error_code: str, proposed_action: str) -> bool:
    """Checks if the proposed action matches the expected action for the scenario."""
    data = pd.read_excel("the_nano_gang\\corpus\\dishwasher_scenarios.xlsx")
    scenario = data.loc[data["error_code"] == error_code]
    if scenario.empty:
        return False
    expected_action = scenario.iloc[0]["correct_action"].strip().lower()
    return proposed_action.strip().lower() == expected_action

# Confirmation criteria for actions
confirmation_criteria = "Do you want to proceed with this action?"

root_agent = Agent(
    model='gemini-2.5-flash',
    name='technician_agent',
    description="Troubleshoots broken dishwashers",
    instruction="""You are a helpful assistant that helps to troubleshoot a broken dishwasher: the Bosch 800 series.
    Ask the user troubleshoot questions until you are certain of the correct action.
    Correct action must be an action from the possible actions list.
    When you are certain propose a correct action and wait for confirmation of the user.
    Literally state the proposed action. For example: 'proposed action: replace_motor'.
    """,
    tools=[
        lookup_error_code,
        possible_actions_list,
        FunctionTool(propose_correct_action, require_confirmation=confirmation_criteria),
        evaluate_action, google_search
    ],
)
# # Confirmation criteria for actions
# confirmation_criteria = "Do you want to proceed with this action?"
#
# root_agent = Agent(
#     model='gemini-2.5-flash',
#     name='technician_agent',
#     description="Troubleshoots broken dishwashers",
#     instruction="""You are a helpful assistant that helps to troubleshoot a broken dishwasher: the Bosch 800 series.
#     Ask the user troubleshoot questions until you are certain of the correct action.
#     Correct action must be an action from the possible actions list.
#     When you are certain propose a correct action and wait for confirmation of the user.
#     Literally state the proposed action. For example: 'proposed action: replace_motor'.
#     """,
#     tools=[
#         lookup_error_code,
#         possible_actions_list,
#         FunctionTool(propose_correct_action, require_confirmation=confirmation_criteria)
#     ],
# )
