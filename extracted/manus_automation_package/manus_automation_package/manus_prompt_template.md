# Manus Prompt Template for Nurse CE Requirements

Use this template when prompting Manus to research and document continuing education requirements for nurses in a specific state.

## Basic Prompt Structure

```
Research and document the continuing education requirements for [LICENSE_TYPE] ([FULL_LICENSE_NAME]) in [STATE] using the enhanced schema v2.1.

Follow these steps:
1. Research the CE requirements by visiting the [STATE] Board of Nursing website and other authoritative sources
2. Document all requirements using the enhanced schema v2.1 structure
3. Include detailed information about:
   - Total CE hours required
   - Renewal cycle
   - Mandatory topics
   - Approved providers
   - Course approval processes
   - Cross-state equivalency where applicable
4. Save the completed JSON file to: [OUTPUT_FILENAME]

Use the enhanced schema structure that includes the course catalog section, provider-course relationships, and all other enhanced features.

[CONTEXT_REFERENCE]
```

## Example Filled Template

```
Research and document the continuing education requirements for RN (Registered Nurse) in California using the enhanced schema v2.1.

Follow these steps:
1. Research the CE requirements by visiting the California Board of Nursing website and other authoritative sources
2. Document all requirements using the enhanced schema v2.1 structure
3. Include detailed information about:
   - Total CE hours required
   - Renewal cycle
   - Mandatory topics
   - Approved providers
   - Course approval processes
   - Cross-state equivalency where applicable
4. Save the completed JSON file to: /home/ubuntu/nurse_ce_requirements/california_rn_ce_requirements_enhanced.json

Use the enhanced schema structure that includes the course catalog section, provider-course relationships, and all other enhanced features.

For context, you previously completed the requirements for RN in New York. You can reference that work for structure and cross-state equivalency information.
```

## Key Elements to Include

1. **Specific License Type**: Always specify both the abbreviation and full name (e.g., "RN (Registered Nurse)")

2. **Clear Research Instructions**: Direct Manus to use authoritative sources, especially the state board website

3. **Schema Compliance**: Emphasize using the enhanced schema v2.1 structure

4. **Output Location**: Provide a specific file path following the naming convention

5. **Context Reference**: When applicable, reference previously completed states/licenses

## Additional Instructions for Complex States

For states with complex requirements, you may want to add specific guidance:

```
Pay special attention to:
- [STATE]'s unique requirements for [SPECIFIC_REQUIREMENT]
- The approval process for [SPECIFIC_COURSE_TYPE] courses
- Cross-state recognition agreements with [NEIGHBORING_STATES]
- Special requirements for [SPECIFIC_PRACTICE_SETTINGS]
```

## Instructions for Territories

For U.S. territories, modify the prompt slightly:

```
Research and document the continuing education requirements for [LICENSE_TYPE] ([FULL_LICENSE_NAME]) in [TERRITORY], a U.S. territory, using the enhanced schema v2.1.

Follow these steps:
1. Research the CE requirements by visiting the [TERRITORY] Board of Nursing website and other authoritative sources
2. Document all requirements using the enhanced schema v2.1 structure, adapting as needed for territorial regulations
3. Include detailed information about:
   [STANDARD_ELEMENTS]
4. Pay special attention to how [TERRITORY] requirements relate to mainland U.S. requirements
5. Save the completed JSON file to: [OUTPUT_FILENAME]
```

## Handling Compact States

For states participating in the Nurse Licensure Compact (NLC), add:

```
Since [STATE] is a member of the Nurse Licensure Compact, please document:
- How CE requirements apply to nurses with a multistate license
- Whether [STATE] recognizes CE completed in other compact states
- Any compact-specific requirements or exemptions
```

## Conclusion

This template provides a consistent structure for prompting Manus to research nurse CE requirements across all states. The automation script will generate appropriate prompts based on this template, but you can customize it as needed for specific situations.
