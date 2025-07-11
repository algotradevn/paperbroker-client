import uuid
import quickfix as fix
import quickfix44 as fix44


class OrderManager:
    def __init__(self, logger):
        self.logger = logger
        self.session_id = None
        self.clord_map = {}  # ord_id -> cl_ord_id
        self.order_info = {}  # cl_ord_id -> dict (symbol, qty, side, ...)
        self.status_map = {}  # cl_ord_id -> status
        self.order_id_map = {}  # cl_ord_id -> ord_id

    def set_session(self, session_id):
        self.session_id = session_id

    def generate_ord_id(self):
        return str(uuid.uuid4())[:8]

    def place_order(self, symbol, side, qty, price, ord_type="LIMIT", tif="GTC"):
        if not self.session_id:
            raise RuntimeError("FIX session is not established.")

        cl_ord_id = self.generate_ord_id()

        order = fix44.NewOrderSingle()
        order.setField(fix.ClOrdID(cl_ord_id))
        order.setField(fix.Symbol(symbol))
        order.setField(fix.SecurityExchange("HSX"))
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

        self.order_info[cl_ord_id] = {"symbol": symbol, "side": side, "qty": qty}
        self.status_map[cl_ord_id] = "PendingNew"
        return cl_ord_id

    def cancel_order(self, cl_ord_id):
        if cl_ord_id not in self.order_id_map:
            raise Exception(f"Unknown cl_ord_id: {cl_ord_id}")
        if not self.session_id:
            raise RuntimeError("FIX session is not established.")

        cancel_cl_ord_id = f"{cl_ord_id}-CXL"
        ord_id = self.order_id_map[cl_ord_id]
        info = self.order_info[cl_ord_id]

        cancel = fix44.OrderCancelRequest()
        cancel.setField(fix.OrigClOrdID(cl_ord_id))
        cancel.setField(fix.ClOrdID(cancel_cl_ord_id))
        cancel.setField(fix.OrderID(ord_id))  # Use original server order ID
        cancel.setField(fix.Symbol(info["symbol"]))
        cancel.setField(fix.SecurityExchange("HSX"))
        cancel.setField(
            fix.Side(fix.Side_BUY if info["side"] == "BUY" else fix.Side_SELL)
        )
        cancel.setField(fix.OrderQty(info["qty"]))
        cancel.setField(fix.TransactTime())

        if fix.Session.sendToTarget(cancel, self.session_id):
            self.logger.debug(f"[ORDER] Sent cancel request: {cancel_cl_ord_id}")
        else:
            self.logger.error("Failed to send cancel request")

        self.status_map[cl_ord_id] = "PendingCancel"

    def on_execution_report(self, message):
        try:
            cl_ord_id = message.getField(fix.ClOrdID().getTag())
            ord_status = message.getField(fix.OrdStatus().getTag())
            ord_id = message.getField(fix.OrderID().getTag())

            self.order_id_map[cl_ord_id] = ord_id

            if ord_id:
                self.clord_map[ord_id] = cl_ord_id

            if ord_status in ["4", "6"]:
                orig_cl_ord_id = message.getField(fix.OrigClOrdID().getTag())
                self.status_map[orig_cl_ord_id] = self.map_status(ord_status)
                self.logger.debug(
                    f"[STATUS] Order {orig_cl_ord_id} is now {self.status_map[orig_cl_ord_id]}"
                )
            else:
                self.status_map[cl_ord_id] = self.map_status(ord_status)
                self.logger.debug(
                    f"[STATUS] Order {cl_ord_id} is now {self.status_map[cl_ord_id]}"
                )

        except Exception as e:
            self.logger.error(f"Failed to process execution report: {e}")

    def get_order_status(self, cl_ord_id):
        return self.status_map.get(cl_ord_id, "Unknown")

    def map_status(self, fix_status):
        return {
            "0": "New",
            "1": "PartiallyFilled",
            "2": "Filled",
            "4": "Canceled",
            "6": "PendingCancel",
            "8": "Rejected",
        }.get(fix_status, "Unknown")
