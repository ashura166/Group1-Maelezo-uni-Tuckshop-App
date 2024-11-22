import tkinter as tk
from tkinter import messagebox
from firebase_config import db

# Firebase references
items_ref = db.collection('items')
offers_ref = db.collection('offers')
purchases_ref = db.collection('purchases')

# Admin credentials
admin_username = "Admin"
admin_password = "1234"

class TuckShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tuck Shop Admin")
        self.root.configure(bg='light blue')  # Set the background color of the main window

        self.login_frame = tk.Frame(self.root, bg='light blue')
        self.login_frame.place(relx=0.5, rely=0.5, anchor='center')

        self.username_label = tk.Label(self.login_frame, text="Admin Username:", bg='light blue', font=('Arial', 16))
        self.username_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.username_entry = tk.Entry(self.login_frame, bg='white', font=('Arial', 16), width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self.login_frame, text="Admin Password:", bg='light blue', font=('Arial', 16))
        self.password_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.password_entry = tk.Entry(self.login_frame, show="*", bg='white', font=('Arial', 16), width=30)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.do_login, bg='white')
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.login_message = tk.Label(self.login_frame, text="", fg="red", bg='light blue')
        self.login_message.grid(row=3, column=0, columnspan=2)

    def do_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == admin_username and password == admin_password:
            self.login_frame.place_forget()
            self.create_main_frame()
        else:
            self.login_message.config(text="Invalid credentials. Please try again.")

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.root, bg='light blue')
        self.main_frame.pack(pady=20)

        self.category_label = tk.Label(self.main_frame, text="Select Category:", bg='light blue')
        self.category_label.grid(row=0, column=0, padx=5, pady=5)
        self.category_listbox = tk.Listbox(self.main_frame, bg='white', width=60, height=5)
        self.category_listbox.grid(row=0, column=1, padx=5, pady=5)
        self.category_listbox.bind('<<ListboxSelect>>', self.load_products)

        self.product_listbox = tk.Listbox(self.main_frame, bg='white', width=60, height=10)
        self.product_listbox.grid(row=1, column=0, columnspan=2, pady=10)

        self.purchase_item_name_label = tk.Label(self.main_frame, text="Item Name to Purchase:", bg='light blue')
        self.purchase_item_name_label.grid(row=2, column=0, padx=5, pady=5)
        self.purchase_item_name_entry = tk.Entry(self.main_frame, bg='white')
        self.purchase_item_name_entry.grid(row=2, column=1, padx=5, pady=5)

        self.purchase_quantity_label = tk.Label(self.main_frame, text="Quantity:", bg='light blue')
        self.purchase_quantity_label.grid(row=3, column=0, padx=5, pady=5)
        self.purchase_quantity_entry = tk.Entry(self.main_frame, bg='white')
        self.purchase_quantity_entry.grid(row=3, column=1, padx=5, pady=5)

        self.purchase_item_button = tk.Button(self.main_frame, text="Purchase Item", command=self.purchase_item, bg='white')
        self.purchase_item_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.delete_item_button = tk.Button(self.main_frame, text="Delete Item", command=self.delete_item, bg='white')
        self.delete_item_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.purchase_message = tk.Label(self.main_frame, text="", fg="green", bg='light blue')
        self.purchase_message.grid(row=6, column=0, columnspan=2)

        self.offers_label = tk.Label(self.main_frame, text="Offers:", bg='light blue')
        self.offers_label.grid(row=7, column=0, padx=5, pady=5)
        self.offers_listbox = tk.Listbox(self.main_frame, bg='white', width=60, height=5)
        self.offers_listbox.grid(row=7, column=1, padx=5, pady=5)

        self.load_categories()
        self.load_offers()

        # Set up Firestore snapshot listeners
        self.setup_listeners()

    def setup_listeners(self):
        items_ref.on_snapshot(self.on_items_snapshot)
        offers_ref.on_snapshot(self.on_offers_snapshot)

    def on_items_snapshot(self, col_snapshot, changes, read_time):
        self.load_products()

    def on_offers_snapshot(self, col_snapshot, changes, read_time):
        self.load_offers()

    def load_categories(self):
        self.category_listbox.delete(0, tk.END)
        categories = items_ref.stream()
        category_set = set()
        for item in categories:
            item_data = item.to_dict()
            category_set.add(item_data['category'])
        category_set.discard('Snacks')  # Remove the 'Snacks' category
        for category in category_set:
            self.category_listbox.insert(tk.END, category)

    def load_products(self, event=None):
        selected_category = self.category_listbox.get(tk.ACTIVE)
        self.product_listbox.delete(0, tk.END)
        products = items_ref.where('category', '==', selected_category).stream()
        for product in products:
            product_data = product.to_dict()
            self.product_listbox.insert(tk.END, f"{product_data['name']} - {product_data['price']}")

    def load_offers(self):
        self.offers_listbox.delete(0, tk.END)
        offers = offers_ref.stream()
        for offer in offers:
            offer_data = offer.to_dict()
            self.offers_listbox.insert(tk.END, offer_data['description'])

    def add_item(self):
        name = self.item_name_entry.get()
        price = self.item_price_entry.get()
        category = self.item_category_entry.get()
        if name and price and category:
            items_ref.add({
                'name': name,
                'price': price,
                'category': category
            })
            self.item_name_entry.delete(0, tk.END)
            self.item_price_entry.delete(0, tk.END)
            self.item_category_entry.delete(0, tk.END)
            self.load_categories()

    def delete_item(self):
        selected_item = self.product_listbox.get(tk.ACTIVE)
        if selected_item:
            item_name = selected_item.split(' - ')[0]
            items = items_ref.where('name', '==', item_name).stream()
            for item in items:
                items_ref.document(item.id).delete()
            self.load_products()
            messagebox.showinfo("Success", "Item deleted successfully")
        else:
            messagebox.showwarning("Warning", "No item selected")

    def purchase_item(self):
        item_name = self.purchase_item_name_entry.get()
        quantity = int(self.purchase_quantity_entry.get())
        items = items_ref.where('name', '==', item_name).stream()
        for item in items:
            item_data = item.to_dict()
            total_price = int(item_data['price'].split()[1]) * quantity
            purchase = {
                'item_id': item.id,
                'item_name': item_data['name'],
                'quantity': quantity,
                'total_price': f"Ksh {total_price}"
            }
            purchases_ref.add(purchase)
            self.purchase_message.config(text=f"Purchase successful! Total price: {purchase['total_price']}")
            self.purchase_item_name_entry.delete(0, tk.END)
            self.purchase_quantity_entry.delete(0, tk.END)
            return
        self.purchase_message.config(text="Item not found.")

if __name__ == '__main__':
    root = tk.Tk()
    app = TuckShopApp(root)
    root.mainloop()
