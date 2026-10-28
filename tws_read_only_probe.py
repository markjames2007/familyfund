"""Minimal read-only TWS API connectivity probe.

Requests account summary, positions, and executions, then disconnects.  It does
not contain order-placement, amendment, or cancellation calls.
"""

from __future__ import annotations

import threading
from collections import Counter

from ibapi.client import EClient
from ibapi.execution import ExecutionFilter
from ibapi.wrapper import EWrapper


class ReadOnlyProbe(EWrapper, EClient):
    def __init__(self) -> None:
        EClient.__init__(self, self)
        self.finished = threading.Event()
        self.positions = 0
        self.executions = 0
        self.summary_fields: set[str] = set()
        self.completions: set[str] = set()

    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        # TWS uses several informational codes; report all messages for setup diagnosis.
        print(f"TWS message [{errorCode}]: {errorString}")

    def nextValidId(self, orderId: int):
        print("Connected to TWS. Sending read-only requests...")
        self.reqAccountSummary(
            9001,
            "All",
            "NetLiquidation,TotalCashValue,BuyingPower,AvailableFunds",
        )
        self.reqPositions()
        self.reqExecutions(9002, ExecutionFilter())

    def accountSummary(self, reqId, account, tag, value, currency):
        self.summary_fields.add(tag)
        print(f"Account summary: {tag} = {value} {currency}".rstrip())

    def accountSummaryEnd(self, reqId: int):
        self.completions.add("summary")
        self._finish_if_ready()

    def position(self, account, contract, position, avgCost):
        self.positions += 1
        print(
            f"Position: {contract.symbol} {contract.secType} "
            f"quantity={position} average_cost={avgCost}"
        )

    def positionEnd(self):
        self.completions.add("positions")
        self._finish_if_ready()

    def execDetails(self, reqId, contract, execution):
        self.executions += 1
        print(
            f"Execution: {execution.time} {execution.side} "
            f"{execution.shares} {contract.symbol} at {execution.price}"
        )

    def execDetailsEnd(self, reqId: int):
        self.completions.add("executions")
        self._finish_if_ready()

    def _finish_if_ready(self):
        if {"summary", "positions", "executions"}.issubset(self.completions):
            self.finished.set()


def main() -> None:
    app = ReadOnlyProbe()
    app.connect("127.0.0.1", 7496, clientId=73)
    network_thread = threading.Thread(target=app.run, daemon=True)
    network_thread.start()

    if not app.finished.wait(timeout=25):
        missing = {"summary", "positions", "executions"} - app.completions
        print(f"Timed out waiting for: {', '.join(sorted(missing))}")

    print(
        f"Read-only probe complete: {len(app.summary_fields)} summary fields, "
        f"{app.positions} positions, {app.executions} executions."
    )
    app.disconnect()


if __name__ == "__main__":
    main()
