# Graylog Cloud template repository

A Template repository enables us to: Copy entire repository Directory structure and files to a brand new repository.

We create Github repository template based on this repository.

Currently [creating a repository from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template) does not extends to settings, only repository structure. Please adjust repository settings as soon as created it from the template:

**Pull Requests:**
`When merging pull requests, you can allow any combination of merge commits, squashing, or rebasing. At least one option must be enabled. If you have linear history requirement enabled on any protected branch, you must enable squashing or rebasing.`

- [ ] Enable "Allow rebase merging"
- [ ] Disable "Allow merge commits"
- [ ] Disable "Allow squash merging"

## Access Management

- [ ] From the "Collaborators and teams" section add `@graylog-cloud-operations` team and grant `write` access.
- [ ] Grant admin role to @Fagani Hajizada and @Andrii Andrieiev.

## Branch protection rules

From the "Code and automation" section choose "Branches" and create a new branch protection rule:

- [ ] Branch name pattern: `main`
- [ ] Enable "Require a pull request before merging"
  - [ ] Require approvals (number of approvals: `2`)
- [ ] Include administrators

## Github Actions

This repository includes two github workflow:

- Ansible linting
- Terraform check formatting/linting

Note: If your new project does not require these workflows please delete or disable them.

## Slack notifications

We currently use the slack channel #team-cloud-ops-notifications to subscribe our Github repositories and receive notifications for `issues, pulls, releases, deployments`.
Please execute these commands in #team-cloud-ops-notifications channel to enable subscription:

``` bash
/github subscribe [REPO_URL]
/github unsubscribe [REPO_URL] commits
```

## Additional notes

- [Cloud Operations Team](https://graylogdocumentation.atlassian.net/wiki/spaces/CLS/pages/2362867732/Team)
- Our [Code Style Guide](https://graylogdocumentation.atlassian.net/wiki/spaces/CLS/pages/1068957823/Code+Style+Guide)
- Our [Patterns for git commit messages and PR descriptions
](https://graylogdocumentation.atlassian.net/wiki/spaces/CLS/pages/2349334533/Patterns+for+git+commit+messages+and+PR+descriptions)
- How do we do Code Reviews? - [Code review guide](https://graylogdocumentation.atlassian.net/wiki/spaces/CLS/pages/1680375817/Code+Review+Guide+-+How+do+we+do+Code+Reviews)
