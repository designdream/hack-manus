#!/usr/bin/env python3
"""
Manus CE Requirements Automation Script

This script automates the process of researching and documenting continuing education
requirements for nurses across all U.S. states using the enhanced schema.

Usage:
  python manus_ce_automation.py --state "State Name" --license_type "RN" [--output_dir "/path/to/output"]

Requirements:
  - Python 3.6+
  - requests
  - json
  - argparse
  - os
"""

import argparse
import json
import os
import sys
from datetime import datetime

def load_state_prioritization():
    """Load the state prioritization list."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prioritization_file = os.path.join(script_dir, "state_prioritization_list.json")
    
    try:
        with open(prioritization_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading state prioritization list: {e}")
        sys.exit(1)

def load_schema():
    """Load the enhanced global schema."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    schema_file = os.path.join(script_dir, "enhanced_global_schema_v2.1.json")
    
    try:
        with open(schema_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schema: {e}")
        sys.exit(1)

def get_next_state_license_pair(current_state=None, current_license_type=None):
    """
    Determine the next state and license type to process based on the prioritization list.
    
    Args:
        current_state: The state that was just processed
        current_license_type: The license type that was just processed
        
    Returns:
        tuple: (next_state, next_license_type)
    """
    prioritization = load_state_prioritization()
    
    # Flatten the state groups into a single ordered list
    all_states = []
    for group in prioritization["state_priority_groups"]:
        all_states.extend(group["states"])
    
    # Get ordered list of license types
    license_types = sorted(
        prioritization["nursing_license_types"],
        key=lambda x: x["priority"]
    )
    license_type_names = [lt["type"] for lt in license_types]
    
    # If no current state/license, start with the first
    if current_state is None or current_license_type is None:
        return (all_states[0], license_type_names[0])
    
    # Find current position
    try:
        state_idx = all_states.index(current_state)
        license_idx = license_type_names.index(current_license_type)
        
        # Try next license type for current state
        if license_idx < len(license_type_names) - 1:
            return (current_state, license_type_names[license_idx + 1])
        
        # Move to next state, first license type
        if state_idx < len(all_states) - 1:
            return (all_states[state_idx + 1], license_type_names[0])
        
        # We've processed everything
        return (None, None)
    
    except ValueError:
        # If state or license not found, start from beginning
        return (all_states[0], license_type_names[0])

def create_output_filename(state, license_type, output_dir):
    """Create standardized output filename."""
    state_slug = state.lower().replace(" ", "_")
    license_slug = license_type.lower().replace("/", "_")
    
    return os.path.join(
        output_dir,
        f"{state_slug}_{license_slug}_ce_requirements_enhanced.json"
    )

def create_task_prompt(state, license_type, output_filename, previous_state=None, previous_license=None):
    """
    Create a prompt for Manus to research and document CE requirements.
    
    Args:
        state: The state to research
        license_type: The license type to research
        output_filename: Where to save the results
        previous_state: The previously processed state (for context)
        previous_license: The previously processed license type (for context)
        
    Returns:
        str: Formatted prompt for Manus
    """
    prompt = f"""
Research and document the continuing education requirements for {license_type} ({get_license_full_name(license_type)}) in {state} using the enhanced schema v2.1.

Follow these steps:
1. Research the CE requirements by visiting the {state} Board of Nursing website and other authoritative sources
2. Document all requirements using the enhanced schema v2.1 structure
3. Include detailed information about:
   - Total CE hours required
   - Renewal cycle
   - Mandatory topics
   - Approved providers
   - Course approval processes
   - Cross-state equivalency where applicable
4. Save the completed JSON file to: {output_filename}

Use the enhanced schema structure that includes the course catalog section, provider-course relationships, and all other enhanced features.
"""

    if previous_state and previous_license:
        prompt += f"""
For context, you previously completed the requirements for {previous_license} in {previous_state}. You can reference that work for structure and cross-state equivalency information.
"""

    return prompt

def get_license_full_name(license_type):
    """Get the full name of a license type."""
    prioritization = load_state_prioritization()
    
    for lt in prioritization["nursing_license_types"]:
        if lt["type"] == license_type:
            return lt["full_name"]
    
    return license_type

def create_progress_tracker(output_dir):
    """Create or update a progress tracking file."""
    tracker_file = os.path.join(output_dir, "ce_requirements_progress.json")
    
    prioritization = load_state_prioritization()
    all_states = []
    for group in prioritization["state_priority_groups"]:
        all_states.extend([(state, group["group_name"]) for state in group["states"]])
    
    license_types = [lt["type"] for lt in prioritization["nursing_license_types"]]
    
    # Create tracking structure
    tracker = {
        "last_updated": datetime.now().isoformat(),
        "total_combinations": len(all_states) * len(license_types),
        "completed_combinations": 0,
        "progress_by_state": {},
        "progress_by_license": {},
        "completed_items": [],
        "pending_items": []
    }
    
    # Initialize state tracking
    for state, group in all_states:
        if state not in tracker["progress_by_state"]:
            tracker["progress_by_state"][state] = {
                "group": group,
                "total": len(license_types),
                "completed": 0,
                "license_types_completed": []
            }
    
    # Initialize license tracking
    for lt in license_types:
        tracker["progress_by_license"][lt] = {
            "total": len(all_states),
            "completed": 0,
            "states_completed": []
        }
    
    # Initialize pending items
    for state, group in all_states:
        for lt in license_types:
            tracker["pending_items"].append({
                "state": state,
                "license_type": lt,
                "output_file": create_output_filename(state, lt, output_dir)
            })
    
    # Write tracker file
    with open(tracker_file, 'w') as f:
        json.dump(tracker, f, indent=2)
    
    return tracker_file

def update_progress_tracker(tracker_file, state, license_type):
    """Update the progress tracker after completing a state/license combination."""
    try:
        with open(tracker_file, 'r') as f:
            tracker = json.load(f)
        
        # Update completion counts
        tracker["completed_combinations"] += 1
        tracker["last_updated"] = datetime.now().isoformat()
        
        # Update state progress
        if state in tracker["progress_by_state"]:
            tracker["progress_by_state"][state]["completed"] += 1
            tracker["progress_by_state"][state]["license_types_completed"].append(license_type)
        
        # Update license progress
        if license_type in tracker["progress_by_license"]:
            tracker["progress_by_license"][license_type]["completed"] += 1
            tracker["progress_by_license"][license_type]["states_completed"].append(state)
        
        # Move from pending to completed
        for i, item in enumerate(tracker["pending_items"]):
            if item["state"] == state and item["license_type"] == license_type:
                completed_item = tracker["pending_items"].pop(i)
                tracker["completed_items"].append(completed_item)
                break
        
        # Write updated tracker
        with open(tracker_file, 'w') as f:
            json.dump(tracker, f, indent=2)
            
        return True
    
    except Exception as e:
        print(f"Error updating progress tracker: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Automate CE requirements research for nurses')
    parser.add_argument('--state', type=str, help='State to process')
    parser.add_argument('--license_type', type=str, help='License type to process')
    parser.add_argument('--output_dir', type=str, default=os.getcwd(), help='Output directory')
    parser.add_argument('--init', action='store_true', help='Initialize progress tracker only')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Copy schema file to output directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    schema_file = os.path.join(script_dir, "enhanced_global_schema_v2.1.json")
    output_schema_file = os.path.join(args.output_dir, "enhanced_global_schema_v2.1.json")
    
    if not os.path.exists(output_schema_file):
        try:
            with open(schema_file, 'r') as src, open(output_schema_file, 'w') as dst:
                dst.write(src.read())
            print(f"Copied schema to {output_schema_file}")
        except Exception as e:
            print(f"Error copying schema: {e}")
    
    # Initialize progress tracker
    tracker_file = create_progress_tracker(args.output_dir)
    print(f"Created progress tracker: {tracker_file}")
    
    if args.init:
        print("Initialization complete. Run again with --state and --license_type to process a specific combination.")
        return
    
    if not args.state or not args.license_type:
        print("Please specify --state and --license_type")
        return
    
    # Create output filename
    output_filename = create_output_filename(args.state, args.license_type, args.output_dir)
    
    # Get previous state/license for context
    with open(tracker_file, 'r') as f:
        tracker = json.load(f)
    
    previous_state = None
    previous_license = None
    
    if tracker["completed_items"]:
        last_completed = tracker["completed_items"][-1]
        previous_state = last_completed["state"]
        previous_license = last_completed["license_type"]
    
    # Create prompt
    prompt = create_task_prompt(
        args.state, 
        args.license_type, 
        output_filename,
        previous_state,
        previous_license
    )
    
    # Print prompt for Manus
    print("\n" + "="*80)
    print("MANUS PROMPT:")
    print("="*80)
    print(prompt)
    print("="*80 + "\n")
    
    # Determine next state/license to process
    next_state, next_license = get_next_state_license_pair(args.state, args.license_type)
    
    if next_state and next_license:
        print(f"After completing this task, the next state/license to process will be: {next_state} - {next_license}")
    else:
        print("This is the final state/license combination to process.")
    
    # Instructions for updating progress
    print("\nAfter Manus completes this task, update the progress tracker with:")
    print(f"python manus_ce_automation.py --state \"{args.state}\" --license_type \"{args.license_type}\" --output_dir \"{args.output_dir}\"")
    
    # Instructions for next task
    if next_state and next_license:
        print("\nThen start the next task with:")
        print(f"python manus_ce_automation.py --state \"{next_state}\" --license_type \"{next_license}\" --output_dir \"{args.output_dir}\"")

if __name__ == "__main__":
    main()
