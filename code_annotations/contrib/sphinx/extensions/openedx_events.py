"""
Sphinx extension for viewing openedx events annotations.
"""
import os

from docutils import nodes
from sphinx.util.docutils import SphinxDirective

from code_annotations.contrib.config import OPENEDX_EVENTS_ANNOTATIONS_CONFIG_PATH

from .base import find_annotations


def find_events(source_path):
    """
    Find the events as defined in the configuration file.

    Return:
        events (dict): found events indexed by event type.
    """
    return find_annotations(
        source_path, OPENEDX_EVENTS_ANNOTATIONS_CONFIG_PATH, ".. event_type:"
    )


class OpenedxEvents(SphinxDirective):
    """
    Sphinx directive to list the events in a single documentation page.

    Use this directive as follows::

        .. openedxevents::

    This directive supports the following configuration parameters:

    - ``openedxevents_source_path``: absolute path to the repository file tree. E.g:

        openedxevents_source_path = os.path.join(os.path.dirname(__file__), "..", "..")

    - ``openedxevents_repo_url``: Github repository where the code is hosted. E.g:

        openedxevents_repo_url = "https://github.com/openedx/myrepo"

    - ``openedxevents_repo_version``: current version of the git repository. E.g:

        import git
        try:
            repo = git.Repo(search_parent_directories=True)
            openedxevents_repo_version = repo.head.object.hexsha
        except git.InvalidGitRepositoryError:
            openedxevents_repo_version = "main"
    """

    required_arguments = 0
    optional_arguments = 0
    option_spec = {}

    def run(self):
        """
        Public interface of the Directive class.

        Return:
            nodes (list): nodes to be appended to the resulting document.
        """
        return list(self.iter_nodes())

    def iter_nodes(self):
        """
        Iterate on the docutils nodes generated by this directive.
        """
        events = find_events(self.env.config.openedxevents_source_path)

        current_domain = ""
        domain_header = None
        current_subject = ""
        subject_header = None

        for event_type in sorted(events):
            domain = event_type.split(".")[2]
            subject = event_type.split(".")[3]
            if domain != current_domain:
                if domain_header:
                    yield domain_header

                current_domain = domain
                domain_header = nodes.section("", ids=[f"openedxevent-domain-{domain}"])
                domain_header += nodes.title(text=f"Architectural subdomain: {domain}")
            if subject != current_subject:
                current_subject = subject
                subject_header = nodes.section("", ids=[f"openedxevent-subject"
                                                        f"-{subject}"])
                subject_header += nodes.title(text=f"Subject: {subject}")
                domain_header += subject_header

            event = events[event_type]
            event_name = event[".. event_name:"]
            event_name_literal = nodes.literal(text=event_name)
            event_data = event[".. event_data:"]
            event_data_literal = nodes.literal(text=event_data)
            event_key_field = event.get(".. event_key_field:", "")
            event_key_literal = nodes.literal(text=event_key_field)
            event_description = event[".. event_description:"]

            event_section = nodes.section("", ids=[f"openedxevent-{event_type}"])
            event_section += nodes.title(text=event_type, ids=[f"title-{event_type}"])
            event_section += nodes.paragraph(text=f"Description: "
                                                  f"{event_description}")
            event_section += nodes.paragraph("", "Signal name: ", event_name_literal)
            if event_key_field:
                event_section += nodes.paragraph(
                    "",
                    "Event key field: ",
                    event_key_literal
                )
            event_section += nodes.paragraph("", "Event data: ", event_data_literal)
            event_section += nodes.paragraph(
                text=f"Defined at: {event['filename']} (line"
                     f" {event['line_number']})"
            )

            subject_header += event_section

        if domain_header:
            yield domain_header


def setup(app):
    """
    Declare the Sphinx extension.
    """
    app.add_config_value(
        "openedxevents_source_path",
        os.path.abspath(".."),
        "env",
    )
    app.add_config_value("openedxevents_repo_url", "", "env")
    app.add_config_value("openedxevents_repo_version", "main", "env")
    app.add_directive("openedxevents", OpenedxEvents)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }