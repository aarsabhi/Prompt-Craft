# PromptCraft

PromptCraft is a Streamlit application that helps users refine and enhance their prompts for Large Language Models (LLMs). It provides an intuitive interface for iterative prompt development, version tracking, and prompt management.

## Features

- **Prompt Refinement**: Automatically enhance prompts with better structure, clarity, and context
- **Version History**: Track different versions of your prompts and compare changes
- **Token Counter**: Get real-time token count and cost estimates
- **Export Options**: Save your prompts as plain text or JSON
- **Prompt Library**: Save and manage your favorite prompts
- **Azure OpenAI Integration**: Seamless integration with Azure OpenAI services

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure Azure OpenAI credentials:
   - The app comes pre-configured with the provided Azure OpenAI key
   - You can update the key in the sidebar if needed
   - The API endpoint is set to: https://idpoai.openai.azure.com/

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Enter Your Prompt**:
   - Paste your initial prompt in the left text area
   - Click "Refine Prompt" to generate an enhanced version

2. **Review and Edit**:
   - The refined version appears in the right panel
   - Edit the refined prompt directly if needed
   - View token count and estimated cost

3. **Version Management**:
   - Track different versions in the version history
   - Use the slider to switch between versions
   - Compare changes across iterations

4. **Save and Export**:
   - Save prompts to your library with custom titles
   - Export prompts as plain text or JSON
   - Access saved prompts from the sidebar

## Notes

- The token counter uses the cl100k_base encoding (GPT-4)
- Cost estimates are approximate based on standard Azure OpenAI pricing
- The application maintains state during the session using Streamlit's session state

## Contributing

Feel free to submit issues and enhancement requests! 