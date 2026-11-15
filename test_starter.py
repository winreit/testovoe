import asyncio
from decimal import Decimal

from starter import recommend_price


def test_normal_calculation():
    async def fetch_offers():
        return {
            "status": "success",
            "offers": [
                {"seller": "myshop", "price": Decimal("4300.00"), "delivery_days": 2},
                {"seller": "PARTS", "price": Decimal("4800.00"), "delivery_days": 3},
                {"seller": "SLOW", "price": Decimal("4700.00"), "delivery_days": 8},
            ],
        }

    result = asyncio.run(
        recommend_price(
            fetch_offers,
            current_price=Decimal("4900.00"),
            min_price=Decimal("4500.00"),
        )
    )

    assert result["price"] == Decimal("4728.00")
    assert result["decision"] == "APPLY"


def test_timeout_returns_hold():
    async def slow_fetch():
        await asyncio.sleep(0.05)
        return {"status": "success", "offers": []}

    result = asyncio.run(
        recommend_price(
            slow_fetch,
            current_price=Decimal("100.00"),
            min_price=Decimal("80.00"),
            timeout_s=0.001,
        )
    )

    assert result["price"] == Decimal("100.00")
    assert result["decision"] == "HOLD"
    assert "TimeoutError" in result["reason"]


def test_exactly_thirty_percent_deviation_is_allowed():
    async def fetch_offers():
        return {
            "status": "success",
            "offers": [
                {"seller": "COMPETITOR", "price": Decimal("92.39"), "delivery_days": 1},
            ],
        }

    result = asyncio.run(
        recommend_price(
            fetch_offers,
            current_price=Decimal("70.00"),
            min_price=Decimal("1.00"),
        )
    )

    assert result["price"] == Decimal("91.00")
    assert result["decision"] == "APPLY"


def test_no_eligible_offers_returns_hold_even_below_minimum():
    async def fetch_offers():
        return {
            "status": "success",
            "offers": [
                {"seller": "MYSHOP", "price": Decimal("50.00"), "delivery_days": 1},
                {"seller": "OTHER", "price": Decimal("60.00"), "delivery_days": None},
                {"seller": "SLOW", "price": Decimal("70.00"), "delivery_days": 7},
            ],
        }

    result = asyncio.run(
        recommend_price(
            fetch_offers,
            current_price=Decimal("40.00"),
            min_price=Decimal("55.00"),
        )
    )

    assert result["price"] == Decimal("40.00")
    assert result["decision"] == "HOLD"
