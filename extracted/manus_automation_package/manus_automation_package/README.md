# Nurse CE Requirements Automation Package

This package provides tools and templates for automating the research and documentation of continuing education requirements for nurses across all U.S. states using Manus.

## Package Contents

1. **Automation Script**: `manus_ce_automation.py` - Python script to manage the workflow
2. **Enhanced Schema**: `enhanced_global_schema_v2.1.json` - JSON Schema for CE requirements
3. **State Prioritization**: `state_prioritization_list.json` - Prioritized list of states and license types
4. **Prompt Template**: `manus_prompt_template.md` - Template for Manus prompts
5. **Context Inheritance**: `context_inheritance_instructions.md` - Instructions for Manus context inheritance
6. **Example Files**: `/examples/` - Example JSON files using the enhanced schema

## Quick Start Guide

### Setup

1. Upload this entire package to Manus
2. Create an output directory:
   ```
   mkdir -p /home/ubuntu/nurse_ce_requirements
   ```
3. Initialize the progress tracker:
   ```
   python manus_automation_package/manus_ce_automation.py --init --output_dir "/home/ubuntu/nurse_ce_requirements"
   ```

### Starting the First Task

1. Generate the prompt for the first state/license combination:
   ```
   python manus_automation_package/manus_ce_automation.py --state "California" --license_type "RN" --output_dir "/home/ubuntu/nurse_ce_requirements"
   ```
2. Copy the generated prompt into your conversation with Manus
3. Let Manus complete the research and documentation

### Continuing with Subsequent Tasks

1. After Manus completes a task, update the progress tracker:
   ```
   python manus_automation_package/manus_ce_automation.py --state "California" --license_type "RN" --output_dir "/home/ubuntu/nurse_ce_requirements"
   ```
2. Start the next task with context inheritance (see `context_inheritance_instructions.md`)
3. Generate the prompt for the next state/license combination:
   ```
   python manus_automation_package/manus_ce_automation.py --state "California" --license_type "LPN/LVN" --output_dir "/home/ubuntu/nurse_ce_requirements"
   ```
4. Continue this process until all states and license types are completed

## Detailed Documentation

- **Automation Script**: The Python script manages the workflow, generates prompts, and tracks progress
- **Enhanced Schema**: The JSON Schema defines the structure for documenting CE requirements
- **State Prioritization**: Lists states and license types in priority order for efficient processing
- **Prompt Template**: Provides a consistent structure for prompting Manus
- **Context Inheritance**: Explains how to use Manus's context inheritance feature effectively

## Processing Strategy

The recommended processing strategy follows this order:

1. Complete all RN requirements for high-population states
2. Complete all LPN/LVN requirements for high-population states
3. Complete all APRN requirements for high-population states
4. Continue with medium and lower population states
5. Complete territories last

This strategy ensures the most impactful states and license types are completed first.

## Customization

You can customize the processing order by editing the `state_prioritization_list.json` file. The automation script will use this file to determine the next state/license combination to process.

## Troubleshooting

If you encounter issues:

1. **Context Limitations**: See `context_inheritance_instructions.md` for strategies
2. **Script Errors**: Ensure Python 3.6+ is installed and all files are in the correct locations
3. **Schema Validation**: Verify that generated JSON files conform to the enhanced schema

## Maintenance

After completing all states:

1. Set up a schedule for monthly updates using the monthly update process
2. Prioritize states with recent regulatory changes
3. Use the same context inheritance approach for updates

## Example Usage

```
# Initialize
python manus_automation_package/manus_ce_automation.py --init --output_dir "/home/ubuntu/nurse_ce_requirements"

# First task
python manus_automation_package/manus_ce_automation.py --state "California" --license_type "RN" --output_dir "/home/ubuntu/nurse_ce_requirements"

# After completion, update progress and get next prompt
python manus_automation_package/manus_ce_automation.py --state "California" --license_type "RN" --output_dir "/home/ubuntu/nurse_ce_requirements"
python manus_automation_package/manus_ce_automation.py --state "California" --license_type "LPN/LVN" --output_dir "/home/ubuntu/nurse_ce_requirements"
```

## Support

For questions or assistance, refer to the documentation files included in this package.
