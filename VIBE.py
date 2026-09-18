"""Student Grade Calculator

A menu-driven program that manages student records, calculates test averages,
and assigns letter grades.
"""

from __future__ import annotations

import os
import sys
import termios
import tty

DATA_FILE = "student_grades.txt"


class Student:
    """Represents a single student record."""

    def __init__(self, name: str, student_id: str, test1: float, test2: float, test3: float):
        self.name = name.strip()
        self.student_id = student_id.strip()
        self.test1 = float(test1)
        self.test2 = float(test2)
        self.test3 = float(test3)
        self.average = self.calculate_average()
        self.grade = self.calculate_grade()

    def calculate_average(self) -> float:
        """Calculate the average of the three test scores."""
        return (self.test1 + self.test2 + self.test3) / 3

    def calculate_grade(self) -> str:
        """Determine the letter grade from the average score."""
        avg = self.average_score()
        if avg >= 90:
            return "A"
        if avg >= 80:
            return "B"
        if avg >= 70:
            return "C"
        if avg >= 60:
            return "D"
        return "F"

    def average_score(self) -> float:
        """Return the average score for the student."""
        return self.average

    def to_record(self) -> str:
        """Serialize a student record into pipe-delimited format."""
        return (
            f"{self.name}|{self.student_id}|{self.test1:.2f}|{self.test2:.2f}|{self.test3:.2f}|"
            f"{self.average:.2f}|{self.grade}"
        )

    @classmethod
    def from_record(cls, record_line: str) -> "Student":
        """Create a Student from a saved pipe-delimited record."""
        parts = record_line.strip().split("|")
        if len(parts) != 7:
            raise ValueError("Invalid student record format.")

        name, student_id, test1, test2, test3, average, grade = parts
        student = cls(name, student_id, float(test1), float(test2), float(test3))
        student.average = float(average)
        student.grade = grade
        return student


def validate_score(score: float) -> float:
    """Ensure a test score is between 0 and 100."""
    value = float(score)
    if not 0 <= value <= 100:
        raise ValueError("Scores must be between 0 and 100.")
    return value


def get_float(prompt: str) -> float:
    """Prompt until the user enters a valid float."""
    while True:
        try:
            return validate_score(float(input(prompt)))
        except ValueError:
            print("Please enter a valid score from 0 to 100.")


def save_students(students: list[Student], file_name: str = DATA_FILE) -> None:
    """Save all student records to a pipe-delimited text file."""
    try:
        with open(file_name, "w", encoding="utf-8") as file:
            for student in students:
                file.write(student.to_record() + "\n")
    except OSError as exc:
        print(f"Error saving file: {exc}")


def load_students(file_name: str = DATA_FILE) -> list[Student]:
    """Load all student records from a pipe-delimited text file."""
    students: list[Student] = []
    if not os.path.exists(file_name):
        return students

    try:
        with open(file_name, "r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                try:
                    students.append(Student.from_record(line))
                except ValueError:
                    print(f"Skipping invalid record: {line.strip()}")
    except OSError as exc:
        print(f"Error loading file: {exc}")

    return students


def display_students(students: list[Student]) -> None:
    """Display all students in a formatted table."""
    if not students:
        print("No student records available.")
        return

    headers = ["Name", "ID", "Test 1", "Test 2", "Test 3", "Average", "Grade"]
    rows = []
    for student in students:
        rows.append([
            student.name,
            student.student_id,
            f"{student.test1:.2f}",
            f"{student.test2:.2f}",
            f"{student.test3:.2f}",
            f"{student.average:.2f}",
            student.grade,
        ])

    widths = [len(header) for header in headers]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))

    def format_row(values: list[str]) -> str:
        return " | ".join(value.ljust(widths[i]) for i, value in enumerate(values))

    border = "-+-".join("-" * width for width in widths)
    print(f"+-{border}-+")
    print(f"| {format_row(headers)} |")
    print(f"+-{border}-+")
    for row in rows:
        print(f"| {format_row(row)} |")
    print(f"+-{border}-+")


def class_statistics(students: list[Student]) -> None:
    """Show highest average, lowest average, and class average."""
    if not students:
        print("No student records available.")
        return

    averages = [student.average for student in students]
    highest = max(averages)
    lowest = min(averages)
    class_average = sum(averages) / len(averages)

    print("Class Statistics")
    print(f"Highest Average: {highest:.2f}")
    print(f"Lowest Average: {lowest:.2f}")
    print(f"Class Average: {class_average:.2f}")


def search_student(students: list[Student], name: str) -> list[Student]:
    """Search for a student by name (case-insensitive)."""
    query = name.strip().lower()
    return [student for student in students if query in student.name.lower()]


def read_single_key() -> str:
    """Read a single keypress from the keyboard."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        char = sys.stdin.read(1)
        return char
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def add_student(students: list[Student]) -> None:
    """Prompt the user to add a new student record."""
    name = input("Enter student name: ").strip()
    student_id = input("Enter student ID: ").strip()

    if not name or not student_id:
        print("Name and ID cannot be blank.")
        return

    test1 = get_float("Enter Test 1 score: ")
    test2 = get_float("Enter Test 2 score: ")
    test3 = get_float("Enter Test 3 score: ")

    for student in students:
        if student.student_id == student_id:
            print(f"Student ID {student_id} already exists.")
            return

    student = Student(name, student_id, test1, test2, test3)
    students.append(student)
    print(f"Student {student.name} added successfully.")


def menu() -> None:
    """Display the main menu and handle user input."""
    students = load_students(DATA_FILE)

    while True:
        print("\nStudent Grade Calculator")
        print("1. Add new student")
        print("2. Display all students")
        print("3. Display class statistics")
        print("4. Search student by name")
        print("5. Save records")
        print("6. Exit (ESC)")

        choice = read_single_key()

        if choice == "\x1b":
            save_students(students, DATA_FILE)
            print("\nExiting program. Records saved to student_grades.txt")
            break

        if choice == "1":
            add_student(students)
        elif choice == "2":
            display_students(students)
        elif choice == "3":
            class_statistics(students)
        elif choice == "4":
            name = input("Enter student name to search: ").strip()
            matches = search_student(students, name)
            if not matches:
                print("No matching students found.")
            else:
                display_students(matches)
        elif choice == "5":
            save_students(students, DATA_FILE)
            print(f"Records saved to {DATA_FILE}")
        elif choice == "6":
            save_students(students, DATA_FILE)
            print(f"Records saved to {DATA_FILE}")
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1-6 or press ESC.")


if __name__ == "__main__":
    menu()


