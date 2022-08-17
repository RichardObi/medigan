# -*- coding: utf-8 -*-
# ! /usr/bin/env python
"""Github Model uploader class that uploads the metadata of a new model to the medigan github repository. """

from __future__ import absolute_import

import json
import logging

from github import Github

from ..constants import (
    CONFIG_FILE_KEY_EXECUTION,
    CONFIG_FILE_KEY_PACKAGE_LINK,
    GITHUB_ASSIGNEE,
    GITHUB_REPO,
    GITHUB_TITLE,
)
from ..utils import Utils
from .base_model_uploader import BaseModelUploader


class GithubModelUploader(BaseModelUploader):
    """`GithubModelUploader` class: Pushes the metadata of a user's model to the medigan repo, where it creates a
    dedicated github issue.

    Parameters
    ----------
    model_id: str
        The generative model's unique id
    access_token: str
        a personal access token linked to your github user account, used as means of authentication

    Attributes
    ----------
    model_id: str
        The generative model's unique id
    access_token: str
        a personal access token linked to your github user account, used as means of authentication
    """

    def __init__(
        self,
        model_id: str,
        access_token: str,
    ):
        self.model_id = model_id
        self.access_token = access_token

    def push(
        self,
        metadata: dict,
        package_link: str = None,
        creator_name: str = "n.a.",
        creator_affiliation: str = "n.a.",
        model_description: str = "n.a.",
    ):
        """Upload the model's metadata inside a github issue to the medigan github repository.

        To add your model to medigan, your metadata will be reviewed on Github and added to medigan's official model metadata

        The medigan repository issues page: https://github.com/RichardObi/medigan/issues

        Get your Github access token here: https://github.com/settings/tokens

        Parameters
        ----------
        metadata: dict
            The model's corresponding metadata
        package_link:
            a package link
        creator_name: str
            the creator name that will appear on the corresponding github issue
        creator_affiliation: str
            the creator affiliation that will appear on the corresponding github issue
        model_description: list
            the model_description that will appear on the corresponding github issue

        Returns
        -------
        str
            Returns the url pointing to the corresponding issue on github
        """

        # Check if the package_link is already in the metadata. If not, add it to metadata.
        metadata = self.add_package_link_to_metadata(
            metadata=metadata, package_link=package_link
        )

        # First use pyGithub to create a Github instance based on san access token
        g = Github(self.access_token)
        repo = g.get_repo(GITHUB_REPO)
        logging.debug(f"Repo: {repo}")

        # Create metadata for github issue
        title = f"{GITHUB_TITLE}: {self.model_id}"
        line_break = "\n"
        body = (
            f"{line_break + '**Creator:** ' if creator_name != '' else ''}{creator_name}"
            f"{line_break + '**Affiliation:** ' if creator_affiliation != '' else ''}{creator_affiliation}"
            f"{line_break + '**Description:** ' if model_description != '' else ''}{model_description}"
            f"{line_break} **Stored in:** {package_link}"
            f"{line_break} ### Model Metadata: {line_break} ```json{json.dumps(metadata, indent=3)}"
        )

        # As a logged-in github user, let's now push to medigan repo using pyGithub
        github_issue = repo.create_issue(
            title=title, body=body, assignee=GITHUB_ASSIGNEE
        )
        logging.info(
            f"{self.model_id}: Successfully created github issue in '{GITHUB_REPO}': '{github_issue.html_url}'"
        )
        return github_issue.html_url

    def add_package_link_to_metadata(
        self, metadata: dict, package_link: str = None, is_update_forced: bool = False
    ) -> dict:
        """Update `package_link` in the model's metadata if current `package_link` does not containing a valid url.

        Parameters
        ----------
        metadata: dict
            The model's corresponding metadata
        package_link: str
            the new package link to used to replace the old one
        is_update_forced: bool
            flag to update metadata even though metadata already contains a valid url in its `package_link`

        Returns
        -------
        dict
            Returns the updated metadata dict with replaced `package_link` if replacement was applicable.
        """

        current_pl = None
        try:
            # Get the package link from the metadata object
            current_pl = metadata[self.model_id][CONFIG_FILE_KEY_EXECUTION][
                CONFIG_FILE_KEY_PACKAGE_LINK
            ]
        except Exception as e:
            logging.debug(
                f"{self.model_id}: Package Link could not be located in metadata for key {self.model_id}.{CONFIG_FILE_KEY_EXECUTION}.{CONFIG_FILE_KEY_PACKAGE_LINK}: {e}"
            )

        # Check if the package link in the metadata contains a valid URL
        if (
            current_pl is not None
            and not is_update_forced
            and (
                (Utils.is_url_valid(current_pl) and current_pl.startswith("http"))
                or current_pl.startswith("models/")
            )
        ):
            # If there is already a valid (non-local) url to a zip file,
            # we assume that this URL is validly pointing to the model.
            # Note: The package link can start with models/ indicating that the model is hosted directly in medigan
            # instead of Zenodo, see model 00007 for an example.
            pass
        else:
            # We update the metadata with the retrieved package_link. Note: Also, in case the metadata points to a path on a
            # user's machine, we avoid publishing that path to github issue by making this update.
            try:
                metadata[self.model_id][CONFIG_FILE_KEY_EXECUTION][
                    CONFIG_FILE_KEY_PACKAGE_LINK
                ] = package_link
            except Exception as e:
                logging.warning(
                    f"{self.model_id}: Package Link could not be update in metadata for key {self.model_id}.{CONFIG_FILE_KEY_EXECUTION}.{CONFIG_FILE_KEY_PACKAGE_LINK}: {e}"
                )
            logging.debug(
                f"{self.model_id}: Before creating github issue, updated package link from '{current_pl}' to '{package_link}'"
            )
        return metadata

    def __repr__(self):
        return (
            f"GithubModelUploader(model_id={self.model_id}, metadata={self.metadata})"
        )

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, idx: int):
        raise NotImplementedError
