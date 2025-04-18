# Manus Context Inheritance Instructions

This document provides instructions for effectively using Manus's context inheritance feature to research and document continuing education requirements for nurses across all U.S. states.

## Overview

Manus allows context to be inherited between tasks, enabling you to process all 50+ states and multiple license types efficiently without hitting context limits. The automation package is designed to work with this feature by:

1. Breaking the work into manageable chunks (one state/license type combination per task)
2. Providing relevant context from previous tasks
3. Maintaining a consistent structure across all tasks
4. Tracking progress to ensure complete coverage

## Setting Up Context Inheritance

### Initial Task

For the first task:

1. Upload the entire automation package to Manus
2. Initialize the progress tracker:
   ```
   python manus_automation_package/manus_ce_automation.py --init --output_dir "/home/ubuntu/nurse_ce_requirements"
   ```
3. Start with the first state/license combination:
   ```
   python manus_automation_package/manus_ce_automation.py --state "California" --license_type "RN" --output_dir "/home/ubuntu/nurse_ce_requirements"
   ```
4. Copy the generated prompt into your conversation with Manus

### Subsequent Tasks

For each subsequent task:

1. When starting a new task, mention: "This task inherits files and context from an original task."
2. Specify which files to inherit:
   ```
   Below are files created or edited in the original task:
   * /home/ubuntu/nurse_ce_requirements/enhanced_global_schema_v2.1.json
   * /home/ubuntu/nurse_ce_requirements/ce_requirements_progress.json
   * /home/ubuntu/nurse_ce_requirements/[previously_completed_files].json
   * /home/ubuntu/manus_automation_package/*
   ```
3. Run the automation script to get the next prompt:
   ```
   python manus_automation_package/manus_ce_automation.py --state "[Current State]" --license_type "[Current License]" --output_dir "/home/ubuntu/nurse_ce_requirements"
   ```
4. Copy the generated prompt into your conversation with Manus

## Maximizing Context Efficiency

To ensure Manus can effectively use the inherited context:

1. **Reference Previous Work**: When appropriate, ask Manus to reference previously completed states for structure and cross-state equivalency information.

2. **Focus on One Combination**: Process only one state/license type combination per task to avoid context overflow.

3. **Use Consistent File Naming**: The automation script enforces consistent file naming (e.g., `california_rn_ce_requirements_enhanced.json`).

4. **Update Progress Tracker**: After each task completes, update the progress tracker to maintain an accurate record.

5. **Prioritize Cross-State Information**: Encourage Manus to identify and document cross-state equivalency for courses whenever possible.

## Handling Context Limitations

If you encounter context limitations:

1. **Reduce Inherited Files**: Only inherit the most relevant previous files.

2. **Focus on Schema Structure**: Ensure the schema structure file is always inherited.

3. **Inherit Adjacent States**: Prioritize inheriting files from geographically or regulatorily similar states.

4. **Use Regional Batching**: Process states in regional batches to maximize cross-state equivalency identification.

## Example Context Inheritance Flow

Here's an example of how to process multiple states in sequence:

1. **Task 1**: Process California RN requirements
   - Upload automation package
   - Initialize progress tracker
   - Run script for California RN prompt

2. **Task 2**: Process California LPN/LVN requirements
   - Inherit context from Task 1
   - Run script for California LPN/LVN prompt
   - Reference California RN work for structure

3. **Task 3**: Process California APRN requirements
   - Inherit context from Tasks 1-2
   - Run script for California APRN prompt
   - Reference previous California work

4. **Task 4**: Process Texas RN requirements
   - Inherit context from Tasks 1-3 (focusing on RN requirements)
   - Run script for Texas RN prompt
   - Look for cross-state equivalency with California

Continue this pattern, following the prioritization in the state_prioritization_list.json file.

## Troubleshooting

If Manus has difficulty with context inheritance:

1. **Restart with Essential Context**: Inherit only the schema file and the most recent state/license file.

2. **Provide Manual Context**: Summarize key findings from previous states if full context inheritance isn't working.

3. **Split Regional Batches**: If a regional batch is too large, split it into smaller geographical units.

4. **Focus on Schema Compliance**: Ensure each file strictly follows the enhanced schema structure.

## Conclusion

By following these instructions and using the automation package, you can efficiently process continuing education requirements for nurses across all U.S. states while maintaining context between tasks. The structured approach ensures comprehensive coverage and consistent documentation format.
