import uuid


class Cart:
    def __init__(self, request):
        self.request = request
        self.create_session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.save_session()

    def create_session(self):
        if not self.request.session.session_key:
            self.request.session.create()
        if not self.request.session.get("cart"):
            self.request.session["cart"] = {
                "id": self.request.session.session_key,
                "cart_items": [],
            }
        self.request.session.modified = True

    def delete_session(self):
        self.request.session.delete()

    def save_session(self):
        self.request.session.modified = True

    def add_product(self, cart_item):
        cart_items = self.request.session["cart"]["cart_items"]
        for item in cart_items:
            if (
                item["id"] == cart_item["id"]
                and item.get("variant") == cart_item.get("variant")
                and item["selected_option"] == cart_item.get("selected_option")
            ):
                item["quantity"] += cart_item["quantity"]
                self.save_session()
                return

        cart_item["item_id"] = str(uuid.uuid4())
        cart_items.append(cart_item)
        self.save_session()

    def update_items(self, cart_item):
        self.request.session["cart"]["cart_items"].append(cart_item)
        self.save_session()

    def update_item_qty(self, item_id, qty):
        cart_items = self.request.session["cart"]["cart_items"]
        for item in cart_items:
            if uuid.UUID(item["item_id"]) == item_id:
                item["quantity"] = qty
                self.save_session()
                return

    def get_id(self):
        return self.request.session["cart"]["id"]

    def get_items(self):
        return self.request.session["cart"]["cart_items"]

    def get_total_price(self):
        total_price = 0.00
        for item in self.get_items():
            total_price += float(item["price"]) * float(item["quantity"])
        return total_price

    def get_product_quantity(self, product_id, variant=None):
        cart_items = self.request.session["cart"]["cart_items"]
        total_quantity = 0
        variant_id = variant.id if variant else None
        for item in cart_items:
            if (
                item["id"] == int(product_id)
                and item.get("variant") == variant_id
            ):
                total_quantity += item["quantity"]
        return total_quantity

    def remove_item(self, item_id):
        cart_items = self.request.session["cart"]["cart_items"]
        for item in cart_items:
            if uuid.UUID(item["item_id"]) == item_id:
                cart_items.remove(item)
                self.save_session()
                return
        return
