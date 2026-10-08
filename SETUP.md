# Mohid-Abbas GitHub Profile

## 1. Create the repository

Create a **public** GitHub repository named exactly:

```text
Mohid-Abbas
```

The repository must belong to the `Mohid-Abbas` account.

## 2. Put these files in the repository

Keep the structure shown below:

```text
Mohid-Abbas/
├── README.md
├── profile.json
├── data/
│   └── contributions.json
├── assets/
│   ├── robot/
│   │   └── robot.gif
│   └── heatmap/
│       └── contributions.svg
├── scripts/
│   ├── fetch_contributions.py
│   ├── render_heatmap_svg.py
│   └── requirements-actions.txt
└── .github/
    └── workflows/
        └── update-profile.yml
```

The robot GIF is generated from the 102 SVG frames exported from the animation source. It has a transparent background, so it sits naturally inside the README.

## 3. Push to GitHub

Push everything to the `main` branch.

## 4. Enable contribution updates

Open:

```text
GitHub → Repository → Actions → Update Profile Art → Run workflow
```

The workflow also runs automatically once per day and refreshes:

```text
data/contributions.json
assets/heatmap/contributions.svg
```

## 5. Changing your profile later

Edit `profile.json` for stable profile information and project descriptions.

Edit `README.md` when you want to change the layout/design.

The robot animation does not need to be regenerated unless you want a different robot animation.
