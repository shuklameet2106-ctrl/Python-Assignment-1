import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def grade(mark):
    if mark >= 90:
        return "AA"
    if mark >= 80:
        return "AB"
    if mark >= 70:
        return "BB"
    if mark >= 60:
        return "BC"
    if mark >= 50:
        return "CC"
    if mark >= 40:
        return "DD"
    return "FF"


csv_path = input().strip()
output_folder = input().strip()

os.makedirs(output_folder, exist_ok=True)

data = pd.read_csv(csv_path)
data.columns = [c.strip() for c in data.columns]

subjects = [c for c in data.columns if c.lower() not in ("enrollment", "name")]

for subject in subjects:
    data[subject] = pd.to_numeric(data[subject], errors="coerce")
    data.loc[(data[subject] < 0) | (data[subject] > 100), subject] = float("nan")

data = data.drop_duplicates()

missing = data[subjects].isna().sum()

for subject in subjects:
    data[subject] = data[subject].fillna(round(data[subject].mean(), 2))

data["Average"] = data[subjects].mean(axis=1).round(2)
data["Grade"] = data["Average"].apply(grade)

summary = pd.DataFrame(
    {
        "Subject": subjects,
        "Mean": [round(data[s].mean(), 2) for s in subjects],
        "Median": [data[s].median() for s in subjects],
        "StdDev": [round(data[s].std(), 2) for s in subjects],
        "Min": [data[s].min() for s in subjects],
        "Max": [data[s].max() for s in subjects],
        "MissingFilled": [int(missing[s]) for s in subjects],
    }
)

data.to_csv(os.path.join(output_folder, "cleaned_marks.csv"), index=False)
summary.to_csv(os.path.join(output_folder, "summary.csv"), index=False)

order = ["AA", "AB", "BB", "BC", "CC", "DD", "FF"]
counts = data["Grade"].value_counts().reindex(order, fill_value=0)

plt.figure(figsize=(8, 5))
plt.bar(counts.index, counts.values, color="steelblue")
plt.title("Grade Distribution")
plt.xlabel("Grade")
plt.ylabel("Students")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "grade_distribution.png"))
plt.close()

plt.figure(figsize=(8, 5))
plt.bar(summary["Subject"], summary["Mean"], color="seagreen")
plt.title("Subject-wise Average")
plt.xlabel("Subject")
plt.ylabel("Average Marks")
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "subject_average.png"))
plt.close()

top = data.nlargest(10, "Average").iloc[::-1]
labels = top["name"] if "name" in top.columns else top.iloc[:, 0].astype(str)

plt.figure(figsize=(8, 5))
plt.barh(labels, top["Average"], color="darkorange")
plt.title("Top Performers")
plt.xlabel("Average Marks")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "top_performers.png"))
plt.close()

print("cleaned_marks.csv")
print("summary.csv")
print("grade_distribution.png")
print("subject_average.png")
print("top_performers.png")
