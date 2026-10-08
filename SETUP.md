# Setup

This repository is the `Mohid-Abbas/Mohid-Abbas` profile README repository.

The profile uses two animated GIFs because GitHub's current documentation says SVG files do not support inline scripting or animation when rendered on GitHub. GIF is therefore used for the robot and contribution animation.

The workflow reads the public contribution calendar through GitHub's GraphQL API, renders it into `assets/heatmap/contributions.gif`, and refreshes it daily. It also runs on every push to `main`, so the first graph is generated automatically after you upload the repository.
