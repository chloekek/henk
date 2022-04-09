from flask import Blueprint, render_template

from hanson.database import Transaction
from hanson.http import Response
from hanson.models.market import Market
from hanson.models.outcome import Outcome
from hanson.models.user import User
from hanson.util.decorators import with_tx
from hanson.util.session import get_session_user
from hanson.models.account import MarketAccount

app = Blueprint(name="market", import_name=__name__)


@app.get("/markets")
@with_tx
def route_get_markets(tx: Transaction) -> Response:
    session_user = get_session_user(tx)
    markets = Market.list_all(tx)
    return Response.ok_html(
        render_template(
            "market_index.html",
            session_user=session_user,
            markets=markets,
        )
    )


@app.get("/market/new")
@with_tx
def route_get_market_new(tx: Transaction) -> Response:
    _session_user = get_session_user(tx)
    return Response.internal_error("TODO: Implement new market page.")


@app.post("/market/new")
@with_tx
def route_post_market_new(tx: Transaction) -> Response:
    _session_user = get_session_user(tx)
    return Response.internal_error("TODO: Implement post new market page.")


@app.get("/market/<int:market_id>")
@with_tx
def route_get_market(tx: Transaction, market_id: int) -> Response:
    session_user = get_session_user(tx)

    market = Market.get_by_id(tx, market_id)
    if market is None:
        return Response.not_found("This market does not exist.")

    author = User.get_by_id(tx, market.author_user_id)
    assert author is not None

    outcomes = Outcome.get_all_by_market(tx, market_id)

    # TODO: We might make a single query that gets the pool balances.
    points_account = MarketAccount.expect_points_account(tx, market_id)
    pool_accounts = [
        MarketAccount.expect_pool_account(tx, market_id, outcome.id)
        for outcome in outcomes.outcomes
    ]

    # TODO: Add real probabilities.
    ps = [1 / n for n in range(1, 100)][: len(outcomes.outcomes)]
    total = sum(ps)
    ps = [p / total for p in ps]

    return Response.ok_html(
        render_template(
            "market.html",
            session_user=session_user,
            market=market,
            author=author,
            outcomes=outcomes,
            probabilities=ps,
            capitalization=points_account.balance,
            zip=zip,
        )
    )
