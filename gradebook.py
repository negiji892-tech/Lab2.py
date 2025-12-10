#!/usr/bin/env python3
"""
gradebook.py
Author: [Bhavesh Singh Naula]
Date: [25-11-2025]
Title: GradeBook Analyzer - Programming for Problem Solving using Python
Description: CLI tool to input student marks (manual or CSV), compute stats,
assign grades, filter pass/fail, display table, and optionally export results to CSV.
"""

import csv
import sys
import statistics
from collections import Counter, OrderedDict

# ---------- Helper / Core functions ----------

def load_from_csv(path):
    """Load CSV with two columns: name,marks (header optional). Returns dict {name: score}"""
    data = OrderedDict()
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                print("CSV is empty.")
                return data
            # If header appears non-numeric in marks column, skip it
            start_i = 0
            # Detect header: see if second column of first row can't be converted to float
            try:
                _ = float(rows[0][1])
            except Exception:
                start_i = 1
            for r in rows[start_i:]:
                if len(r) < 2:
                    continue
                name = r[0].strip()
                if name == "":
                    continue
                try:
                    score = float(r[1].strip())
                except Exception:
                    # skip bad rows
                    continue
                data[name] = score
    except FileNotFoundError:
        print(f"File not found: {path}")
    except Exception as e:
        print("Error reading CSV:", e)
    return data

def manual_entry():
    """Allow user to enter at least 1 student, returns dict {name: score}"""
    print("\nManual entry mode. Enter student data. Type DONE to finish.")
    data = OrderedDict()
    while True:
        name = input("Student name (or DONE): ").strip()
        if name.lower() == "done":
            break
        if name == "":
            print("Name cannot be empty.")
            continue
        score_str = input(f"Marks for {name}: ").strip()
        if score_str.lower() == "done":
            break
        try:
            score = float(score_str)
            data[name] = score
        except ValueError:
            print("Please enter a valid number for marks.")
    return data

def calculate_average(marks_dict):
    if not marks_dict:
        return None
    return sum(marks_dict.values()) / len(marks_dict)

def calculate_median(marks_dict):
    if not marks_dict:
        return None
    return float(statistics.median(marks_dict.values()))

def find_max_score(marks_dict):
    if not marks_dict:
        return None, []
    max_score = max(marks_dict.values())
    students = [n for n, s in marks_dict.items() if s == max_score]
    return max_score, students

def find_min_score(marks_dict):
    if not marks_dict:
        return None, []
    min_score = min(marks_dict.values())
    students = [n for n, s in marks_dict.items() if s == min_score]
    return min_score, students

def assign_grades(marks_dict):
    """Return dict {name: grade} with A/B/C/D/F mapping."""
    grades = {}
    for name, score in marks_dict.items():
        grade = ''
        # Using >= boundaries as spec
        if score >= 90:
            grade = 'A'
        elif 80 <= score <= 89.9999:
            grade = 'B'
        elif 70 <= score <= 79.9999:
            grade = 'C'
        elif 60 <= score <= 69.9999:
            grade = 'D'
        else:
            grade = 'F'
        grades[name] = grade
    return grades

def grade_distribution(grades_dict):
    return Counter(grades_dict.values())

def get_pass_fail(marks_dict, threshold=40.0):
    passed = [n for n, s in marks_dict.items() if s >= threshold]
    failed = [n for n, s in marks_dict.items() if s < threshold]
    return passed, failed

def print_table(marks_dict, grades_dict):
    if not marks_dict:
        print("No data to show.")
        return
    # Calculate column widths
    names = list(marks_dict.keys())
    max_name_len = max(len("Name"), max((len(n) for n in names), default=4))
    max_marks_len = max(len("Marks"), 6)
    max_grade_len = max(len("Grade"), 5)
    sep = "-" * (max_name_len + max_marks_len + max_grade_len + 8)
    header = f"{'Name':<{max_name_len}}  {'Marks':>{max_marks_len}}  {'Grade':^{max_grade_len}}"
    print("\n" + header)
    print(sep)
    for name, marks in marks_dict.items():
        grade = grades_dict.get(name, "")
        marks_str = f"{marks:.2f}".rstrip('0').rstrip('.') if isinstance(marks, float) else str(marks)
        print(f"{name:<{max_name_len}}  {marks_str:>{max_marks_len}}  {grade:^{max_grade_len}}")
    print(sep + "\n")

def export_to_csv(marks_dict, grades_dict, out_path):
    try:
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Marks", "Grade"])
            for name, marks in marks_dict.items():
                writer.writerow([name, marks, grades_dict.get(name, "")])
        print(f"Exported results to {out_path}")
    except Exception as e:
        print("Failed to export CSV:", e)

# ---------- CLI Loop ----------

def show_menu():
    print("""
======== GradeBook Analyzer ========
1) Manual entry (type in names & marks)
2) Load from CSV file (path)
3) Load sample CSV (creates sample data in memory)
4) Exit
""")

def run_analysis(marks):
    # marks: OrderedDict {name: score}
    if not marks:
        print("No student data provided. Nothing to analyze.")
        return

    # Stats
    avg = calculate_average(marks)
    med = calculate_median(marks)
    max_score, max_students = find_max_score(marks)
    min_score, min_students = find_min_score(marks)

    # Grades and distribution
    grades = assign_grades(marks)
    dist = grade_distribution(grades)
    passed, failed = get_pass_fail(marks, threshold=40.0)

    # Print summary
    print("\n--- Analysis Summary ---")
    print(f"Total students: {len(marks)}")
    print(f"Average (mean): {avg:.2f}" if avg is not None else "Average: N/A")
    print(f"Median: {med:.2f}" if med is not None else "Median: N/A")
    if max_score is not None:
        print(f"Max score: {max_score}  (Students: {', '.join(max_students)})")
    if min_score is not None:
        print(f"Min score: {min_score}  (Students: {', '.join(min_students)})")

    # Grade distribution print
    print("\nGrade distribution:")
    for g in ['A', 'B', 'C', 'D', 'F']:
        print(f"  {g}: {dist.get(g, 0)}")

    # Pass/Fail
    print(f"\nPassed (>=40): {len(passed)}")
    if passed:
        print("  " + ", ".join(passed))
    print(f"Failed (<40): {len(failed)}")
    if failed:
        print("  " + ", ".join(failed))

    # Results table
    print_table(marks, grades)

    # Option: export
    while True:
        choice = input("Do you want to export the results table to CSV? (y/n): ").strip().lower()
        if choice in ('y', 'yes'):
            out_path = input("Enter output CSV filename (e.g. results.csv): ").strip()
            if out_path == "":
                out_path = "results.csv"
            export_to_csv(marks, grades, out_path)
            break
        elif choice in ('n', 'no'):
            break
        else:
            print("Please enter y or n.")

def create_sample_data():
    """Returns sample OrderedDict with 6 students (for quick testing)"""
    return OrderedDict([
        ("Alice", 78),
        ("Bob", 92),
        ("Charlie", 65),
        ("Deepa", 55),
        ("Esha", 34),
        ("Faiz", 88),
    ])

def main():
    print("Welcome to GradeBook Analyzer!")
    while True:
        show_menu()
        choice = input("Choose an option (1-4): ").strip()
        if choice == '1':
            data = manual_entry()
            run_analysis(data)
        elif choice == '2':
            path = input("Enter CSV file path: ").strip()
            data = load_from_csv(path)
            run_analysis(data)
        elif choice == '3':
            data = create_sample_data()
            print("Loaded sample data (6 students).")
            run_analysis(data)
        elif choice == '4' or choice.lower() in ('exit','quit'):
            print("Exiting. Bye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
