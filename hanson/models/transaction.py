from __future__ import annotations

from decimal import Decimal

from hanson.database import Transaction
from hanson.models.account import UserAccount
from hanson.models.currency import Points


def create_transaction_income(
    tx: Transaction,
    user_id: int,
    amount: Points,
) -> int:
    """
    Create a new transaction that brings `amount` new points into existence and
    puts them in the user's account. If the user has no account yet, one will be
    created.
    """
    account = UserAccount.ensure_points_account(tx, user_id)
    assert isinstance(account.balance, Points)

    with tx.cursor() as cur:
        cur.execute(
            """
            INSERT INTO "transaction" (type) VALUES ('income') RETURNING id;
            """
        )
        transaction_id: int = cur.fetchone()[0]

    with tx.cursor() as cur:
        cur.execute(
            """
            INSERT INTO "mutation" (transaction_id, debit_account_id, amount)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (transaction_id, account.id, amount.amount),
        )
        mutation_id: int = cur.fetchone()[0]

    with tx.cursor() as cur:
        cur.execute(
            """
            INSERT INTO
              "account_balance" (account_id, mutation_id, post_balance)
            VALUES
              ( %(account_id)s
              , %(mutation_id)s
              , COALESCE(account_current_balance(%(account_id)s), 0) + %(amount)s
              )
            RETURNING
              post_balance;
            """,
            {
                "account_id": account.id,
                "mutation_id": mutation_id,
                "amount": amount.amount,
            },
        )
        post_balance: Decimal = cur.fetchone()[0]
        assert amount + account.balance == Points(post_balance)

    return transaction_id