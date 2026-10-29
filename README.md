# sachin-insight
## Vendored resources

- `vendor/public-apis` — git submodule of [public-apis/public-apis](https://github.com/public-apis/public-apis), a curated list of free APIs (see its `README.md`). After cloning this repo, fetch it with:

  ```sh
  git submodule update --init --depth 1 vendor/public-apis
  ```

## OpenSEO

[OpenSEO](https://github.com/every-app/open-seo) (open-source Semrush/Ahrefs alternative) is installed for Claude Code:

- `.mcp.json` registers the hosted OpenSEO MCP server (`https://app.openseo.so/mcp`). The first time a tool is used, sign in to your OpenSEO account through the OAuth prompt (or run `/mcp` to authenticate). Self-hosting instead? Point the URL at your instance's `/mcp`.
- `.claude/skills/` holds its 12 SEO workflow skills (keyword research, SEO audit, competitor analysis, link prospecting, local SEO, AI visibility, reports, and more). See `.claude/skills/openseo/README.md`.
