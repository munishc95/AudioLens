import re

def extract_guest_names(summary):
    """Extract guest names from the summary"""
    guest_pattern = re.compile(r"Guest \d+:.*?\nDesignation & Company: (.*?)\n", re.DOTALL)
    guests = guest_pattern.findall(summary)
    guests = [f"Guest {i+1}: {guest}" for i, guest in enumerate(guests)]
    return guests


def extract_companies(summary):
    """Extract companies from the summary"""
    companies_section = summary.split("LIST OF COMPANIES")[1].split("Sentiment Over Time")[0].strip()
    companies = []
    print(companies_section)
    for line in companies_section.split('\n'):
        companies.append(line.strip())
    return companies


def get_analysis_sections(summary):
    """Extract different sections from stored summary"""
    return {
        "Summary": (
            summary.split("SUMMARY")[1].split("Question and Answer")[0].strip()
            if "SUMMARY" in summary
            else "Audio too short to extract Summary"
        ),
        "Q&A": (
            summary.split("Question and Answer")[1]
            .split("LIST OF COMPANIES")[0]
            .strip()
            if "Question and Answer" in summary
            else "Audio too short to extract Q&A"
        ),
        "Companies": (
            summary.split("LIST OF COMPANIES")[1]
            .split("LIST OF ACTION ITEMS")[0]
            .strip()
            if "LIST OF COMPANIES" in summary
            else "Audio too short to extract list of Companies"
        ),
        "Sentiments": (
            summary.split("Sentiment Over Time")[1]
            .split("Acronyms and Full Forms")[0]
            .strip()
            if "Sentiment Over Time" in summary
            else "Audio too short to extract Sentiments"
        ),
        "Acronyms": (
            summary.split("Acronyms and Full Forms")[1].split("LIST OF ACTION ITEMS")[0].strip()
            .split("Action Items")[0]
            .strip()
            if "Acronyms and Full Forms" in summary
            else "Audio too short to extract Acronyms"
        ),
        "Action Items": (
            summary.split("Action Items")[1]
            if "Action Items" in summary
            else "Audio too short to extract Action Items"
        )
    }
