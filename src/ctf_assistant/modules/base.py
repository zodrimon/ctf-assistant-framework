"""
Base interfaces for the CTF Assistant framework.

This module defines the standard protocol and base classes for
implementing custom investigation modules and complex workflows.
"""

from typing import Any, Dict, Protocol


class Module(Protocol):
    """
    Protocol defining the standard interface for an investigation module.

    A module is responsible for analyzing specific types of evidence and
    extracting relevant information. All new modules must implement this
    interface to be discoverable and executable by the framework.
    """

    def get_name(self) -> str:
        """
        Return the human-readable name of the module.
        """
        ...

    def analyze(self, evidence_path: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Analyze the given evidence and return the results.

        Args:
            evidence_path: The filesystem path to the evidence.
            kwargs: Additional configuration or parameters.

        Returns:
            A dictionary containing structured analysis results.
        """
        ...


class Workflow(Protocol):
    """
    Protocol defining the standard interface for a complex workflow.

    Workflows orchestrate multiple modules, handle branching logic,
    and can interact with AI or RAG layers. Simple workflows can be
    defined in YAML, but workflows with complex logic should implement
    this Python interface.
    """

    def get_name(self) -> str:
        """
        Return the human-readable name of the workflow.
        """
        ...

    def run(self, session: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the workflow.

        Args:
            session: The active investigation Session instance, which provides
                     storage, context, and state persistence.
            kwargs: Additional configuration or parameters.

        Returns:
            A dictionary containing the overall results of the workflow.
        """
        ...
