import uuid
import quickfix as fix
import quickfix44 as fix44



class OrderManager:
    def __init__(self, logger):
        self.logger = logger
        self.session_id = None
        self.clord_map = {}  # ord_id -> cl_ord_id
        self.order_info = {}  # ord_id -> dict (symbol, qty, side, ...)
        self.status_map = {}  # ord_id -> status

    def set_session(self, session_id):
        self.session_id = session_id

    def generate_ord_id(self):
        return str(uuid.uuid4())[:8]

    def place_order(self, symbol, side, qty, price, ord_type="LIMIT", tif="GTC"):
        if not self.session_id:
            raise RuntimeError(
                "FIX session is not established. Logon has not occurred."
            )

        ord_id = self.generate_ord_id()
        cl_ord_id = f"client-{ord_id}"

        msg = fix44.NewOrderSingle()
        header = msg.getHeader()
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        msg.setField(fix.ClOrdID(cl_ord_id))
        msg.setField(fix.Symbol(symbol))
        msg.setField(fix.SecurityExchange("HSX"))
        msg.setField(fix.Side(fix.Side_BUY if side == "BUY" else fix.Side_SELL))
        msg.setField(fix.OrderQty(qty))
        msg.setField(fix.Price(price))
        msg.setField(
            fix.OrdType(
                fix.OrdType_LIMIT if ord_type == "LIMIT" else fix.OrdType_MARKET
            )
        )
        msg.setField(
            fix.TimeInForce(
                fix.TimeInForce_GOOD_TILL_CANCEL
                if tif == "GTC"
                else fix.TimeInForce_IMMEDIATE_OR_CANCEL
            )
        )
        msg.setField(fix.TransactTime())

        fix.Session.sendToTarget(msg, self.session_id)

        self.clord_map[ord_id] = cl_ord_id
        self.order_info[ord_id] = {
            "symbol": symbol,
            "side": side,
            "qty": qty,
        }
        self.status_map[ord_id] = "PendingNew"

        return ord_id

    def cancel_order(self, ord_id):
        if ord_id not in self.clord_map:
            raise Exception(f"Unknown ord_id: {ord_id}")

        cl_ord_id = self.clord_map[ord_id]
        cancel_id = f"{cl_ord_id}-cancel"

        info = self.order_info[ord_id]

        msg = fix44.OrderCancelRequest()
        header = msg.getHeader()
        header.setField(fix.MsgType(fix.MsgType_OrderCancelRequest))
        msg.setField(fix.OrigClOrdID(cl_ord_id))
        msg.setField(fix.ClOrdID(cancel_id))
        msg.setField(fix.Symbol(info["symbol"]))
        msg.setField(fix.SecurityExchange("HSX"))
        msg.setField(fix.Side(fix.Side_BUY if info["side"] == "BUY" else fix.Side_SELL))
        msg.setField(fix.OrderQty(info["qty"]))
        msg.setField(fix.TransactTime())

        fix.Session.sendToTarget(msg, self.session_id)
        self.status_map[ord_id] = "PendingCancel"

    def get_order_status(self, ord_id):
        return self.status_map.get(ord_id, None)

    def on_execution_report(self, message):
        cl_ord_id = message.getField(fix.ClOrdID().getTag())
        ord_status = message.getField(fix.OrdStatus().getTag())

        ord_id = next((k for k, v in self.clord_map.items() if v == cl_ord_id), None)
        if ord_id:
            self.status_map[ord_id] = self.map_status(ord_status)

    def map_status(self, fix_status):
        return {
            "0": "New",
            "1": "PartiallyFilled",
            "2": "Filled",
            "4": "Canceled",
            "8": "Rejected",
        }.get(fix_status, "Unknown")
