import xml.etree.ElementTree as ET
import json
import random
import matplotlib.pyplot as plt
import pandas as pd

xml_file_path = "xml.xml"

try:
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
except FileNotFoundError:
    print(f"Файл {xml_file_path} не найден.")
    exit()
except ET.ParseError:
    print(f"Ошибка в структуре XML-файла {xml_file_path}.")
    exit()

items = []
for offer in root.findall(".//offer"):
    name = offer.find("name").text
    price = float(offer.find("price").text)
    mission = offer.find("./param[@name='Миссия']").text
    items.append({"name": name, "price": price, "mission": mission})

months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
          "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]

sales_data = {}
for item in items:
    sales_data[item["name"]] = {
        "price": item["price"],
        "mission": item["mission"],
        "sales": [random.randint(0, 50) for _ in range(12)],
    }

def predict_sales_13th_month(sales_data):
    predictions = {}
    for name, data in sales_data.items():
        last_three_months = data["sales"][-3:]
        predicted_sales = round(sum(last_three_months) / len(last_three_months))
        predictions[name] = predicted_sales
    return predictions

predictions = predict_sales_13th_month(sales_data)

json_data = {
    "rovers": [
        {
            "name": name,
            "price": data["price"],
            "mission": data["mission"],
            "sales": data["sales"],
            "predicted_sales": predictions[name]
        }
        for name, data in sales_data.items()
    ]
}

json_file_path = "rovers_sales_data.json"
with open(json_file_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)

df = pd.DataFrame({
    "Марсоход": [name for name in sales_data.keys() for _ in range(12)],
    "Месяц": months * len(sales_data),
    "Продажи": [sales for data in sales_data.values() for sales in data["sales"]]
})

sales_table = df.pivot(index="Месяц", columns="Марсоход", values="Продажи")
sales_table.loc["Прогноз"] = [predictions[rover] for rover in sales_table.columns]

print(sales_table.to_string())

fig, ax = plt.subplots(figsize=(12, 6))
bar_width = 0.3
x = range(len(months))

for i, (name, data) in enumerate(sales_data.items()):
    ax.bar([p + bar_width * i for p in x], data["sales"], width=bar_width, label=f"{name} (история)")
    ax.bar(12 + bar_width * i, predictions[name], width=bar_width, label=f"{name} (прогноз)", color='red')

ax.set_title("Динамика продаж марсоходов с прогнозом на 13-й месяц")
ax.set_xlabel("Месяц")
ax.set_ylabel("Количество продаж")
ax.set_xticks([p + bar_width for p in range(13)])
ax.set_xticklabels(months + ["Прогноз"])
ax.legend()
plt.tight_layout()
plt.show()
