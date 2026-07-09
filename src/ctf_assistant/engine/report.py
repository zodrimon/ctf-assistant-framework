from pathlib import Path

from ctf_assistant.engine.session import Session


class ReportRenderer:
    """
    Renders an investigation Session into a human-readable Markdown report.
    """

    def render(self, session: Session) -> str:
        """
        Generate a Markdown string representing the session state and findings.
        """
        lines = [
            "# CTF Investigation Report",
            "",
            f"**Session ID:** `{session.session_id}`",
            f"**Created At:** {session.created_at}",
            f"**Updated At:** {session.updated_at}",
            "",
            "## State Variables",
            "",
        ]

        if not session.state:
            lines.append("*No state variables recorded.*")
        else:
            for key, value in session.state.items():
                lines.append(f"- **{key}:** {value}")

        lines.extend(["", "## Findings", ""])

        if not session.findings:
            lines.append("*No findings recorded.*")
        else:
            for module_name, findings in session.findings.items():
                lines.append(f"### {module_name}")
                lines.append("")
                
                for idx, finding in enumerate(findings, 1):
                    lines.append(f"**Item {idx}:**")
                    if isinstance(finding, dict):
                        for k, v in finding.items():
                            if isinstance(v, str) and "\n" in v:
                                lines.append(f"- **{k}:**\n```text\n{v}\n```")
                            else:
                                lines.append(f"- **{k}:** {v}")
                    else:
                        lines.append(f"- {finding}")
                    lines.append("")

        return "\n".join(lines) + "\n"

    def save(self, session: Session, file_path: str | Path) -> None:
        """
        Render the session and save the Markdown to a file.
        """
        markdown_content = self.render(session)
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
