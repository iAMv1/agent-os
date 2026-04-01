"""
GitHub MCP Connector

GitHub integration via the GitHub CLI (gh) and REST API.
Provides tools for repository management, PRs, issues, and more.
"""

import os
import json
import subprocess
from typing import Any, Dict, List, Optional

from agentos.mcp.connectors import (
    MCPConnector,
    AuthType,
    ConnectorResult,
    ToolDefinition,
    ConnectorState,
)


class GitHubConnector(MCPConnector):
    """
    MCP connector for GitHub integration.

    Tools provided:
    - github_repo_info: Get repository information
    - github_list_prs: List pull requests
    - github_get_pr: Get PR details
    - github_create_pr: Create a pull request
    - github_list_issues: List issues
    - github_get_issue: Get issue details
    - github_create_issue: Create an issue
    - github_add_comment: Add a comment to PR or issue
    - github_list_files: List repository files
    - github_get_file: Get file contents
    - github_search_repos: Search repositories
    - github_search_code: Search code

    Authentication:
    - GitHub token via GITHUB_TOKEN env var or config
    - Uses gh CLI if available, falls back to REST API
    """

    API_BASE = "https://api.github.com"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="github",
            auth_type=AuthType.BEARER_TOKEN,
            config=config or {},
        )
        self._use_cli = False
        self._repo: Optional[str] = None

    async def connect(self) -> ConnectorResult:
        """Initialize GitHub connection."""
        try:
            self.state = ConnectorState.CONNECTING

            token = self.config.get("token") or os.environ.get("GITHUB_TOKEN")
            if not token:
                return ConnectorResult.fail(
                    "GitHub token not found. Set GITHUB_TOKEN env var or pass token in config."
                )

            self.config["token"] = token
            self._repo = self.config.get("repo")

            if self._check_cli():
                self._use_cli = True
            else:
                self._use_cli = False

            self.state = ConnectorState.CONNECTED
            return ConnectorResult.ok(
                output={
                    "connector": "github",
                    "status": "connected",
                    "method": "cli" if self._use_cli else "api",
                },
                metadata={"auth_type": "bearer_token", "repo": self._repo},
            )

        except Exception as e:
            self.state = ConnectorState.ERROR
            return ConnectorResult.fail(f"Failed to connect to GitHub: {str(e)}")

    async def disconnect(self) -> ConnectorResult:
        """Disconnect GitHub client."""
        try:
            self._tools = None
            self._tools_loaded = False
            self.state = ConnectorState.DISCONNECTED
            return ConnectorResult.ok(
                output={"connector": "github", "status": "disconnected"}
            )
        except Exception as e:
            return ConnectorResult.fail(f"Failed to disconnect from GitHub: {str(e)}")

    def _check_cli(self) -> bool:
        """Check if gh CLI is available."""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _run_gh(self, args: List[str], cwd: Optional[str] = None) -> ConnectorResult:
        """Run a gh CLI command."""
        try:
            result = subprocess.run(
                ["gh"] + args,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=cwd,
            )
            if result.returncode != 0:
                return ConnectorResult.fail(
                    f"gh command failed: {result.stderr.strip()}"
                )
            try:
                return ConnectorResult.ok(output=json.loads(result.stdout))
            except json.JSONDecodeError:
                return ConnectorResult.ok(output=result.stdout.strip())
        except subprocess.TimeoutExpired:
            return ConnectorResult.fail("gh command timed out")
        except Exception as e:
            return ConnectorResult.fail(f"gh command error: {str(e)}")

    def _api_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
    ) -> ConnectorResult:
        """Make a GitHub API request."""
        import urllib.request
        import urllib.error

        url = f"{self.API_BASE}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.config.get('token')}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        body = json.dumps(data).encode() if data else None

        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                return ConnectorResult.ok(output=result)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            return ConnectorResult.fail(f"API error {e.code}: {error_body}")
        except Exception as e:
            return ConnectorResult.fail(f"API request failed: {str(e)}")

    def _request(
        self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None
    ) -> ConnectorResult:
        """Use CLI or API based on availability."""
        if self._use_cli:
            return self._run_gh_cli_command(endpoint, method, data)
        return self._api_request(endpoint, method, data)

    def _run_gh_cli_command(
        self, endpoint: str, method: str, data: Optional[Dict[str, Any]]
    ) -> ConnectorResult:
        """Map API-style calls to gh CLI commands."""
        parts = endpoint.strip("/").split("/")
        if len(parts) < 3:
            return ConnectorResult.fail(f"Cannot map endpoint to gh CLI: {endpoint}")

        owner, repo = parts[0], parts[1]
        resource = parts[2] if len(parts) > 2 else ""
        resource_id = parts[3] if len(parts) > 3 else ""

        if resource == "pulls" and not resource_id and method == "GET":
            args = [
                "pr",
                "list",
                "--repo",
                f"{owner}/{repo}",
                "--json",
                "number,title,state,headRefName,baseRefName,author,createdAt",
            ]
            return self._run_gh(args)
        elif resource == "pulls" and resource_id and method == "GET":
            args = [
                "pr",
                "view",
                resource_id,
                "--repo",
                f"{owner}/{repo}",
                "--json",
                "number,title,body,state,headRefName,baseRefName,author,createdAt,comments,reviews",
            ]
            return self._run_gh(args)
        elif resource == "issues" and not resource_id and method == "GET":
            args = [
                "issue",
                "list",
                "--repo",
                f"{owner}/{repo}",
                "--json",
                "number,title,state,author,createdAt,labels",
            ]
            return self._run_gh(args)
        elif resource == "issues" and resource_id and method == "GET":
            args = [
                "issue",
                "view",
                resource_id,
                "--repo",
                f"{owner}/{repo}",
                "--json",
                "number,title,body,state,author,createdAt,comments,labels",
            ]
            return self._run_gh(args)
        else:
            return self._api_request(endpoint, method, data)

    async def get_tools(self) -> List[ToolDefinition]:
        """Return GitHub tools."""
        return [
            ToolDefinition(
                name="github_repo_info",
                description="Get repository information",
                parameters={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in owner/repo format",
                        },
                    },
                    "required": [],
                },
                handler=self._repo_info,
            ),
            ToolDefinition(
                name="github_list_prs",
                description="List pull requests",
                parameters={
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "string",
                            "description": "PR state (open, closed, all)",
                            "default": "open",
                        },
                        "base": {
                            "type": "string",
                            "description": "Filter by base branch",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max PRs to return",
                            "default": 20,
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository in owner/repo format",
                        },
                    },
                    "required": [],
                },
                handler=self._list_prs,
            ),
            ToolDefinition(
                name="github_get_pr",
                description="Get PR details",
                parameters={
                    "type": "object",
                    "properties": {
                        "pr_number": {
                            "type": "integer",
                            "description": "PR number",
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository in owner/repo format",
                        },
                    },
                    "required": ["pr_number"],
                },
                handler=self._get_pr,
            ),
            ToolDefinition(
                name="github_create_pr",
                description="Create a pull request",
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "PR title",
                        },
                        "body": {
                            "type": "string",
                            "description": "PR description",
                        },
                        "head": {
                            "type": "string",
                            "description": "Source branch",
                        },
                        "base": {
                            "type": "string",
                            "description": "Target branch",
                            "default": "main",
                        },
                        "draft": {
                            "type": "boolean",
                            "description": "Create as draft PR",
                            "default": False,
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository in owner/repo format",
                        },
                    },
                    "required": ["title", "head"],
                },
                handler=self._create_pr,
            ),
            ToolDefinition(
                name="github_list_issues",
                description="List issues",
                parameters={
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "string",
                            "description": "Issue state (open, closed, all)",
                            "default": "open",
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by labels",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max issues to return",
                            "default": 20,
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository in owner/repo format",
                        },
                    },
                    "required": [],
                },
                handler=self._list_issues,
            ),
            ToolDefinition(
                name="github_create_issue",
                description="Create an issue",
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Issue title",
                        },
                        "body": {
                            "type": "string",
                            "description": "Issue description",
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Issue labels",
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository in owner/repo format",
                        },
                    },
                    "required": ["title"],
                },
                handler=self._create_issue,
            ),
            ToolDefinition(
                name="github_add_comment",
                description="Add a comment to a PR or issue",
                parameters={
                    "type": "object",
                    "properties": {
                        "issue_number": {
                            "type": "integer",
                            "description": "PR or issue number",
                        },
                        "body": {
                            "type": "string",
                            "description": "Comment body",
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository in owner/repo format",
                        },
                    },
                    "required": ["issue_number", "body"],
                },
                handler=self._add_comment,
            ),
            ToolDefinition(
                name="github_list_files",
                description="List repository files",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list",
                            "default": "",
                        },
                        "branch": {
                            "type": "string",
                            "description": "Branch name",
                            "default": "main",
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository in owner/repo format",
                        },
                    },
                    "required": [],
                },
                handler=self._list_files,
            ),
            ToolDefinition(
                name="github_get_file",
                description="Get file contents",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path",
                        },
                        "branch": {
                            "type": "string",
                            "description": "Branch name",
                            "default": "main",
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository in owner/repo format",
                        },
                    },
                    "required": ["path"],
                },
                handler=self._get_file,
            ),
            ToolDefinition(
                name="github_search_repos",
                description="Search repositories",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                        "sort": {
                            "type": "string",
                            "description": "Sort by (stars, forks, help-wanted-issues, updated)",
                            "default": "stars",
                        },
                        "order": {
                            "type": "string",
                            "description": "Sort order (asc, desc)",
                            "default": "desc",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
                handler=self._search_repos,
            ),
            ToolDefinition(
                name="github_search_code",
                description="Search code across repositories",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                        "repo": {
                            "type": "string",
                            "description": "Limit search to specific repo",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
                handler=self._search_code,
            ),
        ]

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> ConnectorResult:
        """Execute a GitHub tool."""
        check = self._ensure_connected()
        if not check.success:
            return check

        tools = await self._load_tools_if_needed()
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            return ConnectorResult.fail(
                f"Unknown GitHub tool: {tool_name}. Available: {[t.name for t in tools]}"
            )

        try:
            result = await tool.handler(**arguments)
            return result
        except Exception as e:
            return ConnectorResult.fail(f"GitHub tool '{tool_name}' failed: {str(e)}")

    def _get_repo(self, repo: Optional[str] = None) -> str:
        """Get repo string from argument or config."""
        return repo or self._repo or ""

    def _get_endpoint(self, repo: str, path: str) -> str:
        """Build API endpoint."""
        return f"/repos/{repo}/{path}"

    async def _repo_info(self, repo: Optional[str] = None) -> ConnectorResult:
        """Get repository information."""
        r = self._get_repo(repo)
        if not r:
            return ConnectorResult.fail(
                "No repository specified and no default repo configured."
            )
        result = self._request(self._get_endpoint(r, ""))
        return result

    async def _list_prs(
        self,
        state: str = "open",
        base: Optional[str] = None,
        limit: int = 20,
        repo: Optional[str] = None,
    ) -> ConnectorResult:
        """List pull requests."""
        r = self._get_repo(repo)
        if not r:
            return ConnectorResult.fail("No repository specified.")
        endpoint = self._get_endpoint(r, f"pulls?state={state}&per_page={limit}")
        if base:
            endpoint += f"&base={base}"
        return self._request(endpoint)

    async def _get_pr(
        self, pr_number: int, repo: Optional[str] = None
    ) -> ConnectorResult:
        """Get PR details."""
        r = self._get_repo(repo)
        if not r:
            return ConnectorResult.fail("No repository specified.")
        return self._request(self._get_endpoint(r, f"pulls/{pr_number}"))

    async def _create_pr(
        self,
        title: str,
        head: str,
        body: Optional[str] = None,
        base: str = "main",
        draft: bool = False,
        repo: Optional[str] = None,
    ) -> ConnectorResult:
        """Create a pull request."""
        r = self._get_repo(repo)
        if not r:
            return ConnectorResult.fail("No repository specified.")
        data = {"title": title, "head": head, "base": base, "draft": draft}
        if body:
            data["body"] = body
        return self._request(self._get_endpoint(r, "pulls"), method="POST", data=data)

    async def _list_issues(
        self,
        state: str = "open",
        labels: Optional[List[str]] = None,
        limit: int = 20,
        repo: Optional[str] = None,
    ) -> ConnectorResult:
        """List issues."""
        r = self._get_repo(repo)
        if not r:
            return ConnectorResult.fail("No repository specified.")
        endpoint = self._get_endpoint(r, f"issues?state={state}&per_page={limit}")
        if labels:
            endpoint += f"&labels={','.join(labels)}"
        return self._request(endpoint)

    async def _create_issue(
        self,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        repo: Optional[str] = None,
    ) -> ConnectorResult:
        """Create an issue."""
        r = self._get_repo(repo)
        if not r:
            return ConnectorResult.fail("No repository specified.")
        data: Dict[str, Any] = {"title": title}
        if body:
            data["body"] = body
        if labels:
            data["labels"] = labels
        return self._request(self._get_endpoint(r, "issues"), method="POST", data=data)

    async def _add_comment(
        self, issue_number: int, body: str, repo: Optional[str] = None
    ) -> ConnectorResult:
        """Add a comment to a PR or issue."""
        r = self._get_repo(repo)
        if not r:
            return ConnectorResult.fail("No repository specified.")
        data = {"body": body}
        return self._request(
            self._get_endpoint(r, f"issues/{issue_number}/comments"),
            method="POST",
            data=data,
        )

    async def _list_files(
        self,
        path: str = "",
        branch: str = "main",
        repo: Optional[str] = None,
    ) -> ConnectorResult:
        """List repository files."""
        r = self._get_repo(repo)
        if not r:
            return ConnectorResult.fail("No repository specified.")
        return self._request(self._get_endpoint(r, f"contents/{path}?ref={branch}"))

    async def _get_file(
        self, path: str, branch: str = "main", repo: Optional[str] = None
    ) -> ConnectorResult:
        """Get file contents."""
        r = self._get_repo(repo)
        if not r:
            return ConnectorResult.fail("No repository specified.")
        result = self._request(self._get_endpoint(r, f"contents/{path}?ref={branch}"))
        if (
            result.success
            and isinstance(result.output, dict)
            and "content" in result.output
        ):
            import base64

            result.output["decoded_content"] = base64.b64decode(
                result.output["content"]
            ).decode("utf-8")
        return result

    async def _search_repos(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        limit: int = 10,
    ) -> ConnectorResult:
        """Search repositories."""
        return self._request(
            f"/search/repositories?q={query}&sort={sort}&order={order}&per_page={limit}"
        )

    async def _search_code(
        self,
        query: str,
        repo: Optional[str] = None,
        limit: int = 10,
    ) -> ConnectorResult:
        """Search code."""
        q = query
        if repo:
            q += f" repo:{repo}"
        return self._request(f"/search/code?q={q}&per_page={limit}")
