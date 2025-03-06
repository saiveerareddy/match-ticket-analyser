import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox

# Database setup
def init_db():
    conn = sqlite3.connect("ticketing.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tickets (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      event_id INTEGER,
                      sale_date TEXT,
                      price REAL)''')
    conn.commit()
    conn.close()

# CRUD Operations
def add_ticket(event_id, price):
    conn = sqlite3.connect("ticketing.db")
    cursor = conn.cursor()
    sale_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO tickets (event_id, sale_date, price) VALUES (?, ?, ?)",
                   (event_id, sale_date, price))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Ticket added successfully!")
    view_tickets()

def view_tickets():
    conn = sqlite3.connect("ticketing.db")
    df = pd.read_sql_query("SELECT * FROM tickets", conn)
    conn.close()
    for row in tree.get_children():
        tree.delete(row)
    for index, row in df.iterrows():
        tree.insert("", "end", values=(row["id"], row["event_id"], row["sale_date"], row["price"]))

def delete_ticket():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a ticket to delete.")
        return
    ticket_id = tree.item(selected_item, "values")[0]
    conn = sqlite3.connect("ticketing.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Ticket deleted successfully!")
    view_tickets()

# Analyze Ticket Sales
def analyze_ticket_sales():
    event_id = int(event_id_entry.get())
    conn = sqlite3.connect("ticketing.db")
    df = pd.read_sql_query("SELECT sale_date, COUNT(*) as sales FROM tickets WHERE event_id = ? GROUP BY sale_date", conn, params=(event_id,))
    conn.close()
    if df.empty:
        messagebox.showinfo("Info", "No sales data available for this event.")
        return
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    plt.figure(figsize=(10, 5))
    plt.plot(df['sale_date'], df['sales'], marker='o', linestyle='-', color='blue', linewidth=2, markersize=8)
    plt.xlabel("Date", fontsize=12, color='darkblue')
    plt.ylabel("Tickets Sold", fontsize=12, color='darkblue')
    plt.title("Ticket Sales Trend", fontsize=14, color='darkred')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()

# Predict Future Sales
def predict_future_sales():
    event_id = int(event_id_entry.get())
    conn = sqlite3.connect("ticketing.db")
    df = pd.read_sql_query("SELECT sale_date, COUNT(*) as sales FROM tickets WHERE event_id = ? GROUP BY sale_date", conn, params=(event_id,))
    conn.close()
    if df.empty:
        messagebox.showinfo("Info", "No data available for prediction.")
        return
    df['sale_date'] = pd.to_datetime(df['sale_date']).map(datetime.toordinal)
    X = df[['sale_date']].values
    y = df['sales'].values
    model = LinearRegression()
    model.fit(X, y)
    future_dates = np.array([datetime.now().toordinal() + i for i in range(1, 8)]).reshape(-1, 1)
    predictions = model.predict(future_dates)
    future_dates_actual = [datetime.fromordinal(int(date[0])) for date in future_dates]
    plt.figure(figsize=(10, 5))
    plt.plot(future_dates_actual, predictions, marker='o', linestyle='-', color='red', linewidth=2, markersize=8)
    plt.xlabel("Date", fontsize=12, color='darkblue')
    plt.ylabel("Predicted Tickets Sold", fontsize=12, color='darkblue')
    plt.title("Predicted Ticket Sales Trend", fontsize=14, color='darkred')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()

# GUI Setup
root = tk.Tk()
root.title("Match Ticketing Analysis Tool")
root.geometry("600x500")
root.configure(bg="lightgray")

title_label = tk.Label(root, text="Match Ticketing Analysis Tool", font=("Arial", 16, "bold"), fg="white", bg="darkblue")
title_label.pack(fill=tk.X)

tk.Label(root, text="Event ID:", font=("Arial", 12), bg="lightgray").pack()
event_id_entry = tk.Entry(root)
event_id_entry.pack()

tk.Label(root, text="Price:", font=("Arial", 12), bg="lightgray").pack()
price_entry = tk.Entry(root)
price_entry.pack()

tk.Button(root, text="Add Ticket", command=lambda: add_ticket(int(event_id_entry.get()), float(price_entry.get())), bg="green", fg="white", font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Analyze Sales", command=analyze_ticket_sales, bg="blue", fg="white", font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Predict Sales", command=predict_future_sales, bg="orange", fg="white", font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Delete Ticket", command=delete_ticket, bg="red", fg="white", font=("Arial", 12)).pack(pady=5)

tree_frame = tk.Frame(root)
tree_frame.pack()
tree = ttk.Treeview(tree_frame, columns=("ID", "Event ID", "Sale Date", "Price"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Event ID", text="Event ID")
tree.heading("Sale Date", text="Sale Date")
tree.heading("Price", text="Price")
tree.pack()
view_tickets()

root.mainloop()
