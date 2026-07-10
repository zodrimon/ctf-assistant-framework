from pathlib import Path

from ctf_assistant.engine.session import Session


import markdown
from xhtml2pdf import pisa
from io import BytesIO

class ReportRenderer:
    """
    Renders an investigation Session into a human-readable report (Markdown, HTML, PDF).
    """

    def render(self, session: Session) -> str:
        """Alias for backward compatibility"""
        return self.render_markdown(session)

    def render_markdown(self, session: Session) -> str:
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

        return "\n".join(lines)

    def render_html(self, session: Session) -> str:
        """
        Generate an HTML report using the markdown rendering as the source.
        """
        md_text = self.render_markdown(session)
        # Convert markdown to html using the markdown package
        html_body = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])
        
        # Wrap in a simple HTML template with basic styling
        html_doc = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>CTF Investigation Report</title>
            <style>
                body {{ font-family: sans-serif; margin: 2em; line-height: 1.6; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }}
                h3 {{ color: #16a085; }}
                pre {{ background: #f4f4f4; padding: 1em; border-radius: 5px; overflow-x: auto; font-family: monospace; font-size: 12px; }}
                code {{ background: #f4f4f4; padding: 0.2em; border-radius: 3px; font-family: monospace; font-size: 12px; }}
            </style>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """
        return html_doc

    def render_pdf(self, session: Session, output_path: str | Path) -> bool:
        """
        Generate a PDF report and save it to the specified output path.
        Returns True if successful, False otherwise.
        """
        html_content = self.render_html(session)
        
        with open(output_path, "w+b") as result_file:
            # convert HTML to PDF
            pisa_status = pisa.CreatePDF(
                html_content,                # the HTML to convert
                dest=result_file             # file handle to receive result
            )
            
        # return True on success and False on errors
        return not pisa_status.err

    def save(self, session: Session, file_path: str | Path) -> None:
        """
        Render the session and save the Markdown to a file.
        """
        markdown_content = self.render(session)
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
