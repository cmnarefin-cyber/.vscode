# Manual Setup (Direct API)
**Requirements**: You must be a repository admin to complete these steps.

1. Install the Claude GitHub app to your repository: https://github.com/apps/claude
2. Add authentication to your repository secrets:
   - Either `ANTHROPIC_API_KEY` for API key authentication
   - Or `CLAUDE_CODE_OAUTH_TOKEN` for OAuth token authentication
3. Copy the workflow file from `examples/claude.yml` into your repository's `.github/workflows/`

## Using a Custom GitHub App
If you prefer not to install the official Claude app, you can create your own GitHub App to use with this action.

### Quick Setup
1. Create the app via manifest.
2. Generate private key.
3. Add `APP_ID` and `APP_PRIVATE_KEY` to secrets.
