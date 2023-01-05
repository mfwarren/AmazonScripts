# Uses customer email (obscured by amazon) to identify unique customers
# and report on first time vs returning customers monthly
# from https://sellercentral.amazon.com/reportcentral/AFNShipmentReport/1
# export one month at a time (amazon limitation)
# in csv format
# rename the file to match the format 'amazon-fulfilled-report-{year}-{month:02d}.csv'

# run the script: python amazon-repeat-buyers.py
# it creates daily/monthly/quarterly csv files with the data

import csv
from collections import defaultdict
from datetime import datetime


count = 0
customers = set()
wholesale_customers = set()
customer_orders = 0


class Item:
    def __init__(self, name, price, quantity, tax):
        self.name = name
        self.price = float(price)
        self.quantity = int(quantity)
        self.tax = float(tax)

    def cost(self):
        # not counting sales taxes in revenue
        return self.price  # + self.tax


class Order:
    def __init__(
        self, order_id, customer_id, order_date, order_total, tags, is_returning
    ):
        self.order_id = order_id
        self.customer_id = customer_id
        self.order_date = order_date
        self.order_total = order_total
        self.tags = tags
        self.items = []
        self.is_returning = is_returning
        if "amazon" in self.customer_id:
            self.tags += ",amazon"

    def add_item(self, item):
        self.items.append(item)

    def cost(self):
        value = 0
        for item in self.items:
            value += item.cost()
        return value


def main():
    orders = {}

    # important to load this in time order
    for year in [2021, 2022]:
        for month in range(1, 13):
            try:
                with open(
                    f"amazon-fulfilled-report-{year}-{month:02d}.csv",
                    "r",
                    encoding="utf-8-sig",
                ) as csvfile:
                    reader = csv.DictReader(csvfile, dialect="excel")

                    for row in reader:
                        # print(row)
                        if row["Sales Channel"] not in ["Amazon.com"]:
                            # ignore shopify sales that are fulfilled by amazon
                            continue

                        if row["Amazon Order Id"] not in orders:
                            orders[row["Amazon Order Id"]] = Order(
                                row["Amazon Order Id"],
                                row["Buyer Email"],
                                row["Purchase Date"],
                                0,
                                row["Sales Channel"].lower(),
                                row["Buyer Email"] in customers,
                            )
                        customers.add(row["Buyer Email"])
                        orders[row["Amazon Order Id"]].add_item(
                            Item(
                                row["Merchant SKU"],
                                row["Item Price"],
                                row["Shipped Quantity"],
                                row["Item Tax"],
                            )
                        )
            except FileNotFoundError:
                continue

    # by day
    orders_by_day = defaultdict(list)
    for name, order in orders.items():
        orders_by_day[order.order_date[:10]].append(order)
    with open("AMZ Returning vs New Customers - Daily.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "Order Count", "New Customers", "Returning Customers", "Unique Customers", "Repeat customers as % of toal", "Total Sales", "New Customer Sales", "Returning Customer Sales", "Returning Sales %"])
        for date, orders_list in orders_by_day.items():
            total_revenue = sum([o.cost() for o in orders_list])
            returning_revenue = sum([o.cost() for o in orders_list if o.is_returning])
            new_customer_revenue = sum([o.cost() for o in orders_list if not o.is_returning])
            unique_customers = set([o.customer_id for o in orders_list])
            first_time_buyers = len([o for o in orders_list if not o.is_returning])
            return_buyers = len([o for o in orders_list if o.is_returning])
            writer.writerow([date, len(orders_list), first_time_buyers, return_buyers, len(unique_customers), return_buyers / len(unique_customers), total_revenue, new_customer_revenue, returning_revenue, returning_revenue/total_revenue])

    # by month
    orders_by_month = defaultdict(list)
    for name, order in orders.items():
        orders_by_month[order.order_date[:7]].append(order)

    with open("AMZ Returning vs New Customers - Monthly.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Month", "Order Count", "New Customers", "Returning Customers", "Unique Customers", "Repeat customers as % of toal", "Total Sales", "New Customer Sales", "Returning Customer Sales", "Returning Sales %"])
        for month, orders_list in orders_by_month.items():
            total_revenue = sum([o.cost() for o in orders_list])
            returning_revenue = sum([o.cost() for o in orders_list if o.is_returning])
            new_customer_revenue = sum([o.cost() for o in orders_list if not o.is_returning])
            unique_customers = set([o.customer_id for o in orders_list])
            first_time_buyers = len([o for o in orders_list if not o.is_returning])
            return_buyers = len([o for o in orders_list if o.is_returning])
            writer.writerow([month, len(orders_list), first_time_buyers, return_buyers, len(unique_customers), return_buyers / len(unique_customers), total_revenue, new_customer_revenue, returning_revenue, returning_revenue/total_revenue])

    # by quarter
    orders_by_q = defaultdict(list)
    for name, order in orders.items():
        order_date = datetime.fromisoformat(order.order_date[:10])
        quarter_of_the_year = f'{order_date.year}Q{(order_date.month-1)//3+1}'
        orders_by_q[quarter_of_the_year].append(order)

    with open("AMZ Returning vs New Customers - Quarterly.csv", 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Quarter", "Order Count", "New Customers", "Returning Customers", "Unique Customers", "Repeat customers as % of toal", "Total Sales", "New Customer Sales", "Returning Customer Sales", "Returning Sales %"])
        for q, orders_list in orders_by_q.items():
            total_revenue = sum([o.cost() for o in orders_list])
            returning_revenue = sum([o.cost() for o in orders_list if o.is_returning])
            new_customer_revenue = sum([o.cost() for o in orders_list if not o.is_returning])
            unique_customers = set([o.customer_id for o in orders_list])
            first_time_buyers = len([o for o in orders_list if not o.is_returning])
            return_buyers = len([o for o in orders_list if o.is_returning])
            writer.writerow([q, len(orders_list), first_time_buyers, return_buyers, len(unique_customers), return_buyers / len(unique_customers), total_revenue, new_customer_revenue, returning_revenue, returning_revenue/total_revenue])


if __name__ == '__main__':
    main()
