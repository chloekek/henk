# Hanson

Hanson is a [prediction market][prediction-market] app.

 * Self-hosted, free and open-source software.
 * No real money, users trade virtual internet points.
 * Designed for running internal prediction markets in organizations.

## Development

Enter a development environment with [Nix][nix] [2.3][nix-2.3]:

    nix run -c $SHELL

Run the initial database setup:

    tools/run_postgres.py --force-init run/db_dev

    # In a different terminal:
    export PGHOST="$PWD/run/db_dev/socket"
    tools/setup_database.py
    tools/migrate.py migrate latest

    # Now you can Ctrl+C the postgres instance in the other terminal.

Run the app in development mode:

    overmind start

By default Flask will listen on `localhost:5000`.

[prediction-market]: https://en.wikipedia.org/wiki/Prediction_market
[nix]:               https://nixos.org/
[nix-2.3]:           https://releases.nixos.org/?prefix=nix/nix-2.3/

## To do

 * Add a vacuum daemon because autovacuum doesn’t run on insert-only tables.