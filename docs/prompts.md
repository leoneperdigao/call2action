# Prompts Configuration

This document explains the prompts configuration file (`prompts.yaml`) and how to customize it for your needs.

## Overview

The `prompts.yaml` file contains all the AI prompts used by the Call2Action system to generate meeting summaries and extract action items. By externalizing these prompts to a YAML file, you can easily customize and maintain them without modifying the code.

## Prompt Types

### 1. `chunk_summary`
**Purpose**: Summarizes individual chunks of the meeting transcript.

**When it's used**: When processing long transcripts, the system splits them into chunks and summarizes each chunk separately before combining them.

**Customization tips**:
- Adjust the level of detail you want captured
- Add or remove specific bullet points based on your meeting types
- Modify the language requirements if needed

### 2. `group_summary`
**Purpose**: Combines multiple chunk summaries into intermediate summaries.

**When it's used**: For very long meetings, chunk summaries are grouped and combined hierarchically before final summarization.

**Customization tips**:
- This prompt focuses on organizing and deduplicating information
- You can adjust how information should be structured

### 3. `final_summary`
**Purpose**: Creates the final comprehensive meeting summary.

**When it's used**: This is the final step that combines all summaries into a structured meeting report.

**Customization tips**:
- **Section structure**: Modify the sections to match your organization's needs
- **Meeting types**: Adjust language to handle different meeting types (technical, business, planning, etc.)
- **Detail level**: Control how detailed the final summary should be
- **Format**: Change the markdown structure or section headers

**Current sections**:
- Meeting Overview
- Participants
- Key Discussion Points
- Decisions Made
- Action Items
- Open Questions or Concerns

### 4. `action_items`
**Purpose**: Extracts actionable items from the meeting summary.

**When it's used**: After generating the summary, this prompt is used to extract and list specific action items.

**Customization tips**:
- Add or remove types of actions to capture
- Adjust the format of action items
- Change the level of detail required for each action

## How to Modify Prompts

1. **Edit the YAML file**: Open `prompts.yaml` in your editor
2. **Maintain the structure**: Keep the YAML structure intact (key names and `template:` fields)
3. **Test changes**: Run the pipeline on a sample file to verify your changes work as expected

## Best Practices

### Writing Effective Prompts

1. **Be specific**: Clearly state what you want the AI to do
2. **Provide structure**: Use bullet points or numbered lists to organize requirements
3. **Give examples**: If possible, show the format you want
4. **Set constraints**: Clearly state what should NOT be included
5. **Language requirements**: Specify output language if transcripts may be in different languages

### Testing Prompts

After modifying prompts:
1. Test with different types of meetings (technical, business, planning)
2. Test with different lengths (short, medium, long meetings)
3. Check that the structure is consistent
4. Verify that important information is not lost

### Version Control

- Commit prompt changes with clear messages explaining why you changed them
- Document significant changes in your project's changelog
- Consider keeping old versions as backup

## Troubleshooting

### Prompts not loading
- Verify `prompts.yaml` exists in the project root
- Check YAML syntax is valid (use a YAML validator)
- Ensure all required prompt keys exist

### Poor quality summaries
- Make prompts more specific
- Add examples of what you want
- Adjust the level of detail requested
- Ensure constraints are clear

### Missing information
- Review which sections are marked as optional
- Adjust the prompt to emphasize specific types of information
- Consider whether the information exists in the transcript

## Environment Variables

The prompts file location can be configured via environment variable:
```bash
# In your .env file
PROMPTS_FILE=prompts.yaml
```

## Advanced Customization

### Adding New Prompts

If you need to add new prompts for additional features:

1. Add the prompt to `prompts.yaml`:
```yaml
my_new_prompt:
  template: |
    Your prompt text here...
```

2. Add a property to `PromptManager` in `src/call2action/prompts.py`:
```python
@property
def my_new_prompt(self) -> str:
    """Get the my new prompt."""
    return self.get_prompt("my_new_prompt")
```

3. Use it in your code:
```python
prompt_template = ChatPromptTemplate.from_template(
    self.prompt_manager.my_new_prompt
)
```

## Support

For issues or questions about prompts:
1. Check this documentation
2. Review the example output files in the `output/` directory
3. Test with simple, short transcripts first
4. Open an issue in the project repository with examples
