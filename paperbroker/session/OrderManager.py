from datetime import datetime, timezone
import time
import uuid
import quickfix as fix
import quickfix44 as fix44


class OrderManager:
    def __init__(self, logger):
        self.logger = logger
        self.session_id = None
        self.clord_map = {}
        self.order_info = {}
        self.status_map = {}  # cl_ord_id -> {"status": str, "time": datetime}
        self.order_id_map = {}

    def set_session(self, session_id):
        self.session_id = session_id

    def generate_ord_id(self):
        return str(uuid.uuid4())[:8]

    def extract_exchange_and_symbol(self, full_symbol: str):
        """
        Converts 'HSX:MWG' -> ('HSX', 'MWG')
        """
        if ":" not in full_symbol:
            raise ValueError(
                f"Invalid symbol format: {full_symbol}, expected EXCHANGE:SYMBOL"
            )
        exchange, symbol = full_symbol.split(":", 1)
        return exchange, symbol

    def place_order(
        self,
        full_symbol,
        side,
        qty,
        price,
        ord_type="LIMIT",
        tif="GTC",
    ):
        if not self.session_id:
            raise RuntimeError("FIX session is not established.")

        exchange, symbol = self.extract_exchange_and_symbol(full_symbol)
        cl_ord_id = self.generate_ord_id()

        side = side.upper()

        order = fix44.NewOrderSingle()
        order.setField(fix.ClOrdID(cl_ord_id))
        order.setField(fix.Symbol(symbol))  # Keep full symbol for consistency
        order.setField(fix.SecurityExchange(exchange))
        order.setField(fix.Side(fix.Side_BUY if side == "BUY" else fix.Side_SELL))
        order.setField(fix.OrderQty(qty))
        order.setField(fix.Price(price))
        order.setField(
            fix.OrdType(
                fix.OrdType_LIMIT if ord_type == "LIMIT" else fix.OrdType_MARKET
            )
        )
        order.setField(
            fix.TimeInForce(
                fix.TimeInForce_GOOD_TILL_CANCEL
                if tif == "GTC"
                else fix.TimeInForce_IMMEDIATE_OR_CANCEL
            )
        )
        order.setField(fix.TransactTime())

        if fix.Session.sendToTarget(order, self.session_id):
            self.logger.info(f"[ORDER] Sent new order: {cl_ord_id}")
        else:
            self.logger.error("Failed to send order")

        self.order_info[cl_ord_id] = {
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "exchange": exchange,
        }
        self.status_map[cl_ord_id] = {
            "status": "PendingNew",
            "time": datetime.now(timezone.utc),
        }

        return cl_ord_id

    def cancel_order(self, cl_ord_id, timeout=2.0):
        start = datetime.now()
        while cl_ord_id not in self.order_id_map:
            if (datetime.now() - start).total_seconds() > timeout:
                raise Exception(f"Timeout waiting for OrderID for {cl_ord_id}")
        time.sleep(0.05)  # small wait
        if not self.session_id:
            raise RuntimeError("FIX session is not established.")

        cancel_cl_ord_id = f"{cl_ord_id}-CXL"
        ord_id = self.order_id_map[cl_ord_id]
        info = self.order_info[cl_ord_id]

        cancel = fix44.OrderCancelRequest()
        cancel.setField(fix.OrigClOrdID(cl_ord_id))
        cancel.setField(fix.ClOrdID(cancel_cl_ord_id))
        cancel.setField(fix.OrderID(ord_id))
        cancel.setField(fix.Symbol(info["symbol"]))
        cancel.setField(
            fix.SecurityExchange(info.get("exchange", ""))
        )  # fallback empty if missing
        cancel.setField(
            fix.Side(fix.Side_BUY if info["side"] == "BUY" else fix.Side_SELL)
        )
        cancel.setField(fix.OrderQty(info["qty"]))
        cancel.setField(fix.TransactTime())

        if fix.Session.sendToTarget(cancel, self.session_id):
            self.logger.debug(f"[ORDER] Sent cancel request: {cancel_cl_ord_id}")
        else:
            self.logger.error("Failed to send cancel request")

        self.status_map[cl_ord_id] = {
            "status": "PendingCancel",
            "time": datetime.now(timezone.utc),
        }

    def on_execution_report(self, message):
        try:
            msg_type = message.getHeader().getField(fix.MsgType().getTag())
            if msg_type == fix.MsgType_OrderCancelReject:
                cl_ord_id = message.getField(fix.ClOrdID().getTag())
                order_id = (
                    message.getField(fix.OrderID().getTag())
                    if message.isSetField(fix.OrderID().getTag())
                    else "?"
                )
                text = (
                    message.getField(fix.Text().getTag())
                    if message.isSetField(fix.Text().getTag())
                    else "Unknown reason"
                )
                rej_reason = (
                    message.getField(fix.CxlRejReason().getTag())
                    if message.isSetField(fix.CxlRejReason().getTag())
                    else "?"
                )
                self.logger.warning(
                    f"[CANCEL_REJECTED] Cancel for {cl_ord_id} (orderID={order_id}) was rejected (reason={rej_reason}): {text}"
                )
                return

            cl_ord_id = message.getField(fix.ClOrdID().getTag())
            ord_status = message.getField(fix.OrdStatus().getTag())
            exec_type = message.getField(fix.ExecType().getTag())
            ord_id = message.getField(fix.OrderID().getTag())
            transact_time_str = message.getField(fix.TransactTime().getTag())
            transact_time = datetime.strptime(
                transact_time_str, "%Y%m%d-%H:%M:%S.%f"
            ).replace(tzinfo=timezone.utc)

            self.order_id_map[cl_ord_id] = ord_id
            if ord_id:
                self.clord_map[ord_id] = cl_ord_id

            status = self.map_status(ord_status)

            if exec_type == fix.ExecType_REJECTED:
                text = (
                    message.getField(fix.Text().getTag())
                    if message.isSetField(fix.Text().getTag())
                    else "No reason"
                )
                self.logger.warning(
                    f"[REJECTED] Order {cl_ord_id} was rejected: {text}"
                )
            elif exec_type == fix.ExecType_TRADE:
                last_px = float(message.getField(fix.LastPx().getTag()))
                last_qty = float(message.getField(fix.LastQty().getTag()))
                self.logger.info(
                    f"[TRADE] {cl_ord_id}: Traded {last_qty} @ {last_px} at {transact_time.isoformat()}"
                )
            elif exec_type == fix.ExecType_PENDING_CANCEL:
                orig_cl_ord_id = message.getField(fix.OrigClOrdID().getTag())
                self.logger.debug(
                    f"[PENDING_CANCEL] {orig_cl_ord_id} pending cancel at {transact_time.isoformat()}"
                )
            elif exec_type == fix.ExecType_CANCELED:
                orig_cl_ord_id = message.getField(fix.OrigClOrdID().getTag())
                self.logger.info(
                    f"[CANCELED] {orig_cl_ord_id} was canceled at {transact_time.isoformat()}"
                )
            elif exec_type == fix.ExecType_NEW:
                self.logger.info(
                    f"[NEW] Order {cl_ord_id} accepted at {transact_time.isoformat()}"
                )

            if ord_status in ["4", "6"]:
                if message.isSetField(fix.OrigClOrdID().getTag()):
                    orig_cl_ord_id = message.getField(fix.OrigClOrdID().getTag())
                    prev = self.status_map.get(orig_cl_ord_id)
                    if prev is None or transact_time > prev["time"]:
                        self.status_map[orig_cl_ord_id] = {
                            "status": status,
                            "time": transact_time,
                        }
            else:
                prev = self.status_map.get(cl_ord_id)
                if prev is None or transact_time > prev["time"]:
                    self.status_map[cl_ord_id] = {
                        "status": status,
                        "time": transact_time,
                    }

        except Exception as e:
            self.logger.error(f"Failed to process execution report: {e}")

    def get_order_status(self, cl_ord_id):
        entry = self.status_map.get(cl_ord_id)
        return entry["status"] if entry else "Unknown"

    def map_status(self, fix_status):
        return {
            "0": "New",
            "1": "PartiallyFilled",
            "2": "Filled",
            "4": "Canceled",
            "6": "PendingCancel",
            "8": "Rejected",
        }.get(fix_status, "Unknown")
