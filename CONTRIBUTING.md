# Contributing Guidelines

## Preamble

Please take the time to carefully review the sections of this document that pertain
to your specific problem. If you have any other questions to which you couldn't find
and answer here, feel free to use [Discussions / Q&A](https://github.com/Advanced-Systems/anonpy/discussions/categories/q-a)
to seek more help. You may also want to have a look at the [Wiki](https://github.com/Advanced-Systems/anonpy/wiki)
page to learn more about internal development processes.

## Software Development Life Cycle

### Bug Reports

Errors should be submitted on GitHub in [Issues](https://github.com/Advanced-Systems/anonpy/issues).
Try to fill out the bug report template to the best of your knowledge.
Feel free to add additional information that you think could be remotely helpful
for troubleshooting the issue.

### Feature Requests

New feature requests should be filled on GitHub in [Discussions / Feature Requests](https://github.com/Advanced-Systems/anonpy/discussions/categories/feature-requests).
Note that it is is not paramount to write a detailed story about the requested
feature in question, but rather to create an incentive for the community to come
together to iron out the specifics.

A *story* should contain the following headers:

1. **Preamble** - *brief description about the suggested feature and its benifits*
2. **Requirements** - *concise checkboxes for developers for later use in PR reviews*
3. **Remarks** - *some notes or open questions that need to be addressed during development*
4. **Planning Status** - *targeted release version*

Once a feature suggestions has been finalized, it is ready to be converted into
an issue by the Repository owner (`@StefanGreve`).

## Branching Policy

This project uses the [GitHub Flow](https://guides.github.com/introduction/flow/index.html),
i.e. all changes happen through Pull Requests (PRs). Because all PRs should target
the `master` branch, the threshold of acceptance is fairly high.

Avoid long-living feature branches to decrease the probability of merge conflicts.
If possible, divide a story into smaller self-contained chunks of subtasks that
can be merged separately.

### Commit Etiquette

It is recommended to keep all commits [atomic](https://en.wikipedia.org/wiki/Atomic_commit).

Commit messages should always start with a verb in simple present. Good candidates
for this are, i.a.

- Add
- Change
- Fix
- Improve
- Update
- Refactor
- Remove

Good to know: you can attribute co-authors in your commit messages. Learn more about
how to do it [here](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors).

## Code Style

Without going into great lengths, try to take the following advice to heart:

- *use* type annotations for all function parameters (with the exception of `*args`
  and `**kwargs`)
- function names *must* obey the same rules as commit message sentence starters
- functions and classes *must* be annotated by doc strings
