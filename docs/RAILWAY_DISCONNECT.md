# Disconnect Nexus Ignis from Railway

This repository no longer includes Railway-specific deployment files in this branch:

- `Procfile` removed
- `nixpacks.toml` removed

Removing these files stops this repository from advertising Railway-specific deployment commands, but it does not disconnect an existing Railway project from GitHub. That connection lives in your Railway account.

## Disconnect from Railway Dashboard

1. Open Railway.
2. Open the Nexus Ignis project.
3. Open the service connected to this GitHub repository.
4. Go to **Settings**.
5. Find **Source** or **GitHub Repo** connection.
6. Click **Disconnect** or change the source repository.
7. Disable automatic deploys if Railway offers that option.
8. Remove the `DATABASE_URL` variable if the database is no longer used.
9. Delete the Railway service/project only if you are sure you no longer need the hosted app or database.

## GitHub Side Cleanup

If Railway installed a GitHub App:

1. Open GitHub Settings.
2. Go to **Applications**.
3. Open **Installed GitHub Apps**.
4. Find Railway.
5. Remove access to this repository or uninstall the app if no longer needed.

## Important

Before deleting the Railway PostgreSQL database, export or back up any archive data you still need.
