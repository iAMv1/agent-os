"""
AgentOS GitHub Integration System

Uses `gh` CLI for all GitHub operations with:
- Memoized binary resolution
- exec_file_no_throw wrapper (never throws, graceful degradation)
- Authentication handling with fallbacks
- Graceful degradation chains
- All operations return {success, error, output/data}
"""

import os
import re
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from functools import lru_cache


def gh_exe() -> str:
    """Memoized gh binary resolution."""
    return shutil.which("gh") or "gh"


def exec_file_no_throw(
    cmd: List[str],
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """Execute command without throwing. Returns {stdout, stderr, code}."""
    import subprocess

    try:
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        result = subprocess.run(
            cmd,
            cwd=cwd or os.getcwd(),
            env=full_env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Command timed out", "code": -1}
    except FileNotFoundError:
        return {"stdout": "", "stderr": f"Command not found: {cmd[0]}", "code": -1}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "code": -1}


def _normalize_result(
    result: Dict[str, Any],
    success_key: Optional[str] = None,
    data_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Normalize exec_file_no_throw result to {success, error, output/data}."""
    if result["code"] == 0:
        output = result["stdout"].strip()
        try:
            data = json.loads(output)
            return {"success": True, "data": data, "output": output}
        except (json.JSONDecodeError, ValueError):
            return {"success": True, "output": output, "data": None}
    else:
        error = result["stderr"].strip() or "Unknown error"
        return {"success": False, "error": error, "output": result["stdout"].strip()}


@lru_cache(maxsize=10)
def _get_repo_from_remote(cwd: Optional[str] = None) -> Optional[str]:
    """Get current repo in owner/repo format. LRU-cached."""
    r = exec_file_no_throw(
        ["gh", "repo", "view", "--json", "nameWithOwner"],
        cwd=cwd or os.getcwd(),
    )
    if r["code"] == 0:
        try:
            data = json.loads(r["stdout"])
            return data.get("nameWithOwner")
        except (json.JSONDecodeError, KeyError):
            pass
    return None


def gh_auth_status() -> Dict[str, Any]:
    """Check GitHub CLI authentication status."""
    r = exec_file_no_throw(["gh", "auth", "status"])
    if r["code"] == 0:
        return {
            "success": True,
            "authenticated": True,
            "output": r["stdout"].strip(),
        }
    else:
        return {
            "success": False,
            "authenticated": False,
            "error": r["stderr"].strip(),
            "output": r["stdout"].strip(),
        }


def gh_auth_login(token: Optional[str] = None) -> Dict[str, Any]:
    """Authenticate with GitHub. Uses GH_TOKEN env var or provided token."""
    env = None
    if token:
        env = {"GH_TOKEN": token}

    r = exec_file_no_throw(["gh", "auth", "status"], env=env)
    if r["code"] == 0:
        return {"success": True, "authenticated": True}

    if not token:
        return {
            "success": False,
            "error": "Not authenticated. Set GH_TOKEN env var or call gh_auth_login(token)",
        }

    return {
        "success": False,
        "error": "Authentication failed",
        "details": r["stderr"].strip(),
    }


def create_pr(
    title: str,
    body: str,
    base: str = "main",
    head: Optional[str] = None,
    repo: Optional[str] = None,
    draft: bool = False,
    labels: Optional[List[str]] = None,
    assignees: Optional[List[str]] = None,
    reviewers: Optional[List[str]] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a pull request.

    Args:
        title: PR title
        body: PR description/body
        base: Base branch (default: main)
        head: Head branch (default: current branch)
        repo: owner/repo (default: auto-detect)
        draft: Create as draft PR
        labels: List of labels to add
        assignees: List of assignees
        reviewers: List of reviewers
        cwd: Working directory

    Returns:
        {success, data: {number, url, title}, error}
    """
    cmd = ["gh", "pr", "create", "--title", title, "--base", base]

    if head:
        cmd.extend(["--head", head])
    if repo:
        cmd.extend(["--repo", repo])
    if draft:
        cmd.append("--draft")

    # Write body to temp file to avoid shell escaping issues
    body_file = None
    try:
        if body:
            body_file = os.path.join(os.getcwd(), ".pr_body_temp.md")
            with open(body_file, "w", encoding="utf-8") as f:
                f.write(body)
            cmd.extend(["--body-file", body_file])

        if labels:
            cmd.extend(["--label", ",".join(labels)])
        if assignees:
            cmd.extend(["--assignee", ",".join(assignees)])
        if reviewers:
            cmd.extend(["--reviewer", ",".join(reviewers)])

        result = exec_file_no_throw(cmd, cwd=cwd, timeout=60)
        return _normalize_result(result)

    finally:
        if body_file and os.path.exists(body_file):
            try:
                os.remove(body_file)
            except OSError:
                pass


def get_pr(
    pr_number: Optional[int] = None,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get PR details.

    Args:
        pr_number: PR number (default: current branch's PR)
        repo: owner/repo
        cwd: Working directory

    Returns:
        {success, data: {pr details}, error}
    """
    cmd = ["gh", "pr", "view"]

    if pr_number:
        cmd.append(str(pr_number))

    cmd.extend(
        [
            "--json",
            "number,title,body,state,headRefName,baseRefName,url,createdAt,author",
        ]
    )

    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def list_prs(
    state: str = "open",
    base: Optional[str] = None,
    head: Optional[str] = None,
    limit: int = 20,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List pull requests.

    Args:
        state: Filter by state (open, closed, merged, all)
        base: Filter by base branch
        head: Filter by head branch
        limit: Max number of PRs to return
        repo: owner/repo
        cwd: Working directory

    Returns:
        {success, data: [list of PRs], error}
    """
    cmd = [
        "gh",
        "pr",
        "list",
        "--state",
        state,
        "--limit",
        str(limit),
        "--json",
        "number,title,state,headRefName,baseRefName,url,createdAt",
    ]

    if base:
        cmd.extend(["--base", base])
    if head:
        cmd.extend(["--head", head])
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def merge_pr(
    pr_number: int,
    method: str = "merge",
    delete_branch: bool = False,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Merge a pull request.

    Args:
        pr_number: PR number
        method: Merge method (merge, squash, rebase)
        delete_branch: Delete head branch after merge
        repo: owner/repo
        cwd: Working directory

    Returns:
        {success, error, output}
    """
    cmd = ["gh", "pr", "merge", str(pr_number), f"--{method}"]

    if delete_branch:
        cmd.append("--delete-branch")
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def close_pr(
    pr_number: int,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Close a pull request without merging."""
    cmd = ["gh", "pr", "close", str(pr_number)]
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def get_pr_reviews(
    pr_number: int,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get reviews for a PR.

    Returns:
        {success, data: [list of reviews], error}
    """
    cmd = [
        "gh",
        "pr",
        "view",
        str(pr_number),
        "--json",
        "reviews",
        "--jq",
        ".reviews",
    ]
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def add_pr_review(
    pr_number: int,
    action: str = "approve",
    body: Optional[str] = None,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add a review to a PR.

    Args:
        pr_number: PR number
        action: Review action (approve, comment, request_changes)
        body: Review body/comment
        repo: owner/repo
        cwd: Working directory

    Returns:
        {success, error, output}
    """
    cmd = ["gh", "pr", "review", str(pr_number), f"--{action}"]

    if body:
        cmd.extend(["--body", body])
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def request_pr_changes(
    pr_number: int,
    reason: Optional[str] = None,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Request changes on a PR."""
    return add_pr_review(
        pr_number, action="request_changes", body=reason, repo=repo, cwd=cwd
    )


def approve_pr(
    pr_number: int,
    comment: Optional[str] = None,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Approve a PR."""
    return add_pr_review(pr_number, action="approve", body=comment, repo=repo, cwd=cwd)


def add_pr_comment(
    pr_number: int,
    body: str,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add a comment to a PR.

    Returns:
        {success, data: {comment details}, error}
    """
    cmd = ["gh", "pr", "comment", str(pr_number), "--body", body]
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def add_pr_review_comment(
    pr_number: int,
    body: str,
    commit_sha: str,
    path: str,
    line: Optional[int] = None,
    side: str = "RIGHT",
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add an inline review comment on a specific line.

    Args:
        pr_number: PR number
        body: Comment body
        commit_sha: Commit SHA to comment on
        path: File path
        line: Line number
        side: LEFT or RIGHT
        repo: owner/repo
        cwd: Working directory

    Returns:
        {success, data: {comment details}, error}
    """
    cmd = [
        "gh",
        "api",
        f"repos/{_get_repo_from_remote(cwd) or repo}/pulls/{pr_number}/comments",
        "--method",
        "POST",
        "--input",
        "-",
    ]

    payload: Dict[str, Any] = {
        "body": body,
        "commit_id": commit_sha,
        "path": path,
        "side": side,
    }
    if line:
        payload["line"] = line

    result = exec_file_no_throw(
        cmd,
        cwd=cwd,
        env={**os.environ, "GH_INPUT": json.dumps(payload)},
    )
    return _normalize_result(result)


def reply_to_pr_comment(
    pr_number: int,
    comment_id: int,
    body: str,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Reply to an existing PR comment.

    Returns:
        {success, data: {reply details}, error}
    """
    repo_name = repo or _get_repo_from_remote(cwd)
    if not repo_name:
        return {"success": False, "error": "Could not determine repository"}

    cmd = [
        "gh",
        "api",
        f"repos/{repo_name}/pulls/{pr_number}/comments/{comment_id}/replies",
        "--method",
        "POST",
        "--input",
        "-",
    ]

    payload = {"body": body}
    result = exec_file_no_throw(
        cmd,
        cwd=cwd,
        env={**os.environ, "GH_INPUT": json.dumps(payload)},
    )
    return _normalize_result(result)


def get_pr_comments(
    pr_number: int,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Get all comments on a PR."""
    cmd = [
        "gh",
        "pr",
        "view",
        str(pr_number),
        "--json",
        "comments",
        "--jq",
        ".comments",
    ]
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def get_pr_diff(
    pr_number: int,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Get the diff for a PR."""
    cmd = ["gh", "pr", "diff", str(pr_number)]
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    if result["code"] == 0:
        return {"success": True, "output": result["stdout"].strip(), "data": None}
    return {"success": False, "error": result["stderr"].strip(), "output": ""}


def get_pr_files(
    pr_number: int,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Get list of files changed in a PR."""
    cmd = [
        "gh",
        "pr",
        "view",
        str(pr_number),
        "--json",
        "files",
        "--jq",
        ".files",
    ]
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def get_pr_checks(
    pr_number: int,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Get CI check status for a PR."""
    cmd = [
        "gh",
        "pr",
        "checks",
        str(pr_number),
        "--json",
        "name,status,conclusion,detailsUrl",
    ]
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def create_issue(
    title: str,
    body: Optional[str] = None,
    labels: Optional[List[str]] = None,
    assignees: Optional[List[str]] = None,
    milestone: Optional[str] = None,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new issue.

    Args:
        title: Issue title
        body: Issue description
        labels: List of labels
        assignees: List of assignees
        milestone: Milestone title
        repo: owner/repo
        cwd: Working directory

    Returns:
        {success, data: {number, url, title}, error}
    """
    cmd = ["gh", "issue", "create", "--title", title]

    if body:
        cmd.extend(["--body", body])
    if labels:
        cmd.extend(["--label", ",".join(labels)])
    if assignees:
        cmd.extend(["--assignee", ",".join(assignees)])
    if milestone:
        cmd.extend(["--milestone", milestone])
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def get_issue(
    issue_number: int,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Get issue details."""
    cmd = ["gh", "issue", "view", str(issue_number)]
    cmd.extend(
        ["--json", "number,title,body,state,url,createdAt,author,labels,assignees"]
    )
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def list_issues(
    state: str = "open",
    labels: Optional[List[str]] = None,
    assignee: Optional[str] = None,
    limit: int = 20,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List issues.

    Args:
        state: Filter by state (open, closed, all)
        labels: Filter by labels
        assignee: Filter by assignee
        limit: Max issues to return
        repo: owner/repo
        cwd: Working directory

    Returns:
        {success, data: [list of issues], error}
    """
    cmd = [
        "gh",
        "issue",
        "list",
        "--state",
        state,
        "--limit",
        str(limit),
        "--json",
        "number,title,state,url,createdAt,author,labels",
    ]

    if labels:
        cmd.extend(["--label", ",".join(labels)])
    if assignee:
        cmd.extend(["--assignee", assignee])
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def close_issue(
    issue_number: int,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Close an issue."""
    cmd = ["gh", "issue", "close", str(issue_number)]
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def reopen_issue(
    issue_number: int,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Reopen a closed issue."""
    cmd = ["gh", "issue", "reopen", str(issue_number)]
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def add_issue_comment(
    issue_number: int,
    body: str,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a comment to an issue."""
    cmd = ["gh", "issue", "comment", str(issue_number), "--body", body]
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def update_issue(
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    labels: Optional[List[str]] = None,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
    assignees: Optional[List[str]] = None,
    add_assignees: Optional[List[str]] = None,
    remove_assignees: Optional[List[str]] = None,
    milestone: Optional[str] = None,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing issue.

    Args:
        issue_number: Issue number
        title: New title
        body: New body
        labels: Replace all labels
        add_labels: Add these labels
        remove_labels: Remove these labels
        assignees: Replace all assignees
        add_assignees: Add these assignees
        remove_assignees: Remove these assignees
        milestone: New milestone
        repo: owner/repo
        cwd: Working directory

    Returns:
        {success, error, output}
    """
    cmd = ["gh", "issue", "edit", str(issue_number)]

    if title:
        cmd.extend(["--title", title])
    if body:
        cmd.extend(["--body", body])
    if labels:
        cmd.extend(["--label", ",".join(labels)])
    if add_labels:
        cmd.extend(["--add-label", ",".join(add_labels)])
    if remove_labels:
        cmd.extend(["--remove-label", ",".join(remove_labels)])
    if assignees:
        cmd.extend(["--assignee", ",".join(assignees)])
    if add_assignees:
        cmd.extend(["--add-assignee", ",".join(add_assignees)])
    if remove_assignees:
        cmd.extend(["--remove-assignee", ",".join(remove_assignees)])
    if milestone:
        cmd.extend(["--milestone", milestone])
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def search_issues(
    query: str,
    limit: int = 20,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Search issues and PRs."""
    cmd = [
        "gh",
        "search",
        "issues",
        query,
        "--limit",
        str(limit),
        "--json",
        "number,title,state,url,createdAt,author,isPullRequest",
    ]
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def analyze_pr_diff(
    pr_number: int,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze a PR's diff and return structured analysis.

    Returns:
        {success, data: {files_changed, lines_added, lines_deleted, suggestions}, error}
    """
    diff_result = get_pr_diff(pr_number, repo, cwd)
    if not diff_result["success"]:
        return diff_result

    diff_text = diff_result["output"]
    files_result = get_pr_files(pr_number, repo, cwd)

    analysis = {
        "pr_number": pr_number,
        "diff_length": len(diff_text),
        "files_changed": [],
        "lines_added": 0,
        "lines_deleted": 0,
        "suggestions": [],
    }

    if files_result["success"] and files_result["data"]:
        for f in files_result["data"]:
            analysis["files_changed"].append(
                {
                    "path": f.get("path"),
                    "additions": f.get("additions", 0),
                    "deletions": f.get("deletions", 0),
                    "changes": f.get("changes", 0),
                }
            )
            analysis["lines_added"] += f.get("additions", 0)
            analysis["lines_deleted"] += f.get("deletions", 0)

    # Analyze diff for common issues
    if diff_text:
        lines = diff_text.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("+") and not line.startswith("+++"):
                # Check for debug statements
                if re.search(
                    r"(console\.log|print\s*\(|debugger|TODO|FIXME|HACK)",
                    line,
                    re.IGNORECASE,
                ):
                    analysis["suggestions"].append(
                        {
                            "type": "debug_statement",
                            "line": line.strip(),
                            "message": "Possible debug statement left in code",
                        }
                    )
                # Check for very long lines
                if len(line) > 120:
                    analysis["suggestions"].append(
                        {
                            "type": "long_line",
                            "line": i + 1,
                            "message": f"Line too long ({len(line)} chars, max 120)",
                        }
                    )
                # Check for hardcoded secrets patterns
                if re.search(
                    r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
                    line,
                    re.IGNORECASE,
                ):
                    analysis["suggestions"].append(
                        {
                            "type": "possible_secret",
                            "line": line.strip(),
                            "message": "Possible hardcoded secret detected",
                        }
                    )

    return {"success": True, "data": analysis, "output": None}


def generate_pr_review_suggestions(
    pr_number: int,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate review suggestions for a PR.

    Returns:
        {success, data: {review: {suggestions, summary, files_reviewed}}, error}
    """
    analysis = analyze_pr_diff(pr_number, repo, cwd)
    if not analysis["success"]:
        return analysis

    data = analysis["data"]
    suggestions = data.get("suggestions", [])

    summary_parts = []
    summary_parts.append(f"Reviewed {len(data['files_changed'])} files")
    summary_parts.append(f"+{data['lines_added']} -{data['lines_deleted']} lines")

    if suggestions:
        summary_parts.append(f"Found {len(suggestions)} potential issues")
    else:
        summary_parts.append("No obvious issues detected")

    review = {
        "summary": ". ".join(summary_parts),
        "suggestions": suggestions,
        "files_reviewed": [f["path"] for f in data["files_changed"]],
        "stats": {
            "files_changed": len(data["files_changed"]),
            "lines_added": data["lines_added"],
            "lines_deleted": data["lines_deleted"],
            "issues_found": len(suggestions),
        },
    }

    return {"success": True, "data": {"review": review}, "output": None}


def auto_review_pr(
    pr_number: int,
    approve_if_clean: bool = False,
    repo: Optional[str] = None,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Automatically review a PR and optionally approve if clean.

    Args:
        pr_number: PR number
        approve_if_clean: Auto-approve if no issues found
        repo: owner/repo
        cwd: Working directory

    Returns:
        {success, data: {review, action_taken}, error}
    """
    review_result = generate_pr_review_suggestions(pr_number, repo, cwd)
    if not review_result["success"]:
        return review_result

    review = review_result["data"]["review"]
    issues = review.get("suggestions", [])
    action_taken = "reviewed"

    if approve_if_clean and not issues:
        approve_result = approve_pr(
            pr_number,
            comment="Auto-approved: no issues detected",
            repo=repo,
            cwd=cwd,
        )
        if approve_result["success"]:
            action_taken = "approved"

    # Post review as comment if there are issues
    if issues and not approve_if_clean:
        comment_body = "## Auto-Review Results\n\n"
        comment_body += f"**Summary:** {review['summary']}\n\n"
        comment_body += "### Suggestions\n\n"
        for i, suggestion in enumerate(issues, 1):
            comment_body += f"{i}. **{suggestion['type']}**: {suggestion['message']}\n"

        add_pr_comment(pr_number, comment_body, repo, cwd)
        action_taken = "commented"

    return {
        "success": True,
        "data": {
            "review": review,
            "action_taken": action_taken,
        },
    }


def get_repo_info(
    repo: Optional[str] = None, cwd: Optional[str] = None
) -> Dict[str, Any]:
    """Get repository information."""
    cmd = ["gh", "repo", "view"]
    cmd.extend(["--json", "nameWithOwner,url,defaultBranchRef,isPrivate,description"])
    if repo:
        cmd.extend(["--repo", repo])

    result = exec_file_no_throw(cmd, cwd=cwd)
    return _normalize_result(result)


def list_repo_branches(
    repo: Optional[str] = None,
    limit: int = 50,
    cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """List repository branches."""
    cmd = [
        "gh",
        "api",
        f"repos/{repo or _get_repo_from_remote(cwd)}/branches",
        "--paginate",
        "--jq",
        f".[:{limit}] | .[].name",
    ]

    result = exec_file_no_throw(cmd, cwd=cwd)
    if result["code"] == 0:
        branches = [
            b.strip() for b in result["stdout"].strip().split("\n") if b.strip()
        ]
        return {"success": True, "data": branches, "output": None}
    return {"success": False, "error": result["stderr"].strip(), "output": ""}


def get_github_state(cwd: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get aggregate GitHub state (similar to get_git_state).

    Returns comprehensive state or None if not available.
    """
    auth = gh_auth_status()
    if not auth["success"]:
        return None

    repo_info = get_repo_info(cwd=cwd)
    if not repo_info["success"]:
        return None

    data = repo_info.get("data", {})

    prs = list_prs(cwd=cwd)
    issues = list_issues(cwd=cwd)

    return {
        "authenticated": True,
        "repo": data.get("nameWithOwner"),
        "url": data.get("url"),
        "default_branch": data.get("defaultBranchRef", {}).get("name", "main"),
        "is_private": data.get("isPrivate", False),
        "description": data.get("description", ""),
        "open_prs": len(prs["data"]) if prs["success"] and prs["data"] else 0,
        "open_issues": len(issues["data"])
        if issues["success"] and issues["data"]
        else 0,
    }
