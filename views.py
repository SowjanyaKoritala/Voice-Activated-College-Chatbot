from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pandas as pd
import os
from .models import Branch, Timetable

# Load Excel file — ensure the path is correct
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
excel_path = os.path.join(BASE_DIR, 'data', 'VNITSW.xlsx')
df = pd.read_excel(excel_path)

# Preprocess for case-insensitive matching
df['Roll Number'] = df['Roll Number'].astype(str).str.lower()
df['Student Name'] = df['Student Name'].astype(str).str.lower()

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def ask(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('query', '').lower().strip()
        response_parts = []
        # Normalize input
        query_clean = query.replace(" ", "").lower()
        query_parts = query.lower().split()

        def name_matches(row_name):
            row_name_clean = row_name.lower().replace(" ", "")
            if query_clean in row_name_clean:
                return True
            if len(query_parts) >= 2:
                reversed_query = "".join(reversed(query_parts))
                return reversed_query in row_name_clean
            return False

        matched_rows = df[
            df['Roll Number'].str.lower().str.contains(query_clean) |
            df['Roll Number'].str.lower().str[-4:].str.contains(query_clean) |
            df['Student Name'].apply(lambda name: name_matches(str(name)))
        ]
        if not matched_rows.empty:
            for _, row in matched_rows.iterrows():
                student_name = row.get('Student Name', '').strip().title() or "N/A"
                roll_no = row.get('Roll Number', '').strip().upper() or "N/A"
                branch = row.get('Branch', '').strip() or "N/A"

                response_parts.append(
                    f"Name: {student_name}, Roll No: {roll_no}, Branch: {branch}"
                )
        # Greetings
        if any(greet in query for greet in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            response_parts.append("Hi! I am your college assistant 🤖. You can ask me about college info, HODs, courses, fee structure, placements, etc.")

        if "principal" in query:
            response_parts.append("The Principal of Vignan's Nirula Institute is Dr. P. Radhika.")

        if "college name" in query or ("college" in query and "name" in query and "principal" not in query):
            response_parts.append("This is Vignan's Nirula Institute of Technology and Science for Women, Guntur.")

        if "location" in query or "where" in query:
            response_parts.append("The college is located at Palakaluru Road, Guntur, Andhra Pradesh, India.")

        if "affiliation" in query or "university" in query or "affiliated" in query:
            response_parts.append("The college is affiliated with JNTUK (Jawaharlal Nehru Technological University, Kakinada).")

        if "accreditation" in query or "naac" in query or "nba" in query or "status" in query:
            response_parts.append("Vignan's Nirula is accredited by NAAC with 'A++' Grade and has NBA accreditation for select programs.")

        if "vision" in query or "mission" in query:
            response_parts.append(
                "Vision: To empower women through quality technical education.\n"
                "Mission: To foster innovation, leadership, and a learning ecosystem with values and ethics."
            )

        if "facility" in query or "facilities" in query or "infrastructure" in query:
            response_parts.append(
                "Campus includes: Digital Classrooms, Library, Labs, Auditorium, Wi-Fi, "
                "Hostels, Cafeteria, Transport, Sports Complex, and Placement Cell."
            )

        # HODs
        if any(k in query for k in ["hod", "head", "incharge", "lead", "who leads"]):
            departments = {
                "cse": "The HOD of CSE Department is Dr. V. Lakshman Narayana.",
                "ece": "The HOD of ECE Department is Dr. G. Sandhya.",
                "it": "The HOD of IT Department is Dr. K.V.S.S. Ramakrishna.",
                "eee": "The HOD of EEE Department is Dr. R. Srikanth.",
                "aiml": "The HOD of AIML & DS is P. Slipa Chaitanya.",
                "ai": "The HOD of AIML & DS is P. Slipa Chaitanya.",
                "ds": "The HOD of AIML & DS is P. Slipa Chaitanya.",
                "bs and h": "The HOD of Basic Sciences and Humanities is Dr. T.V.N. Prasanna",
            }
            matched = False
            for dept, msg in departments.items():
                if dept in query:
                    response_parts.append(msg)
                    matched = True
                    break
            if not matched:
                response_parts.append("Please specify a valid department to get the HOD details.")

        # Fees
        if "fee" in query or "tuition" in query or "fee structure" in query:
            response_parts.append(
                "Fee Structure:\n"
                "B.Tech: ₹95,000/year\nM.Tech: ₹57,000/year\nDiploma: ₹35,000/year\n"
                "Note: Fees may vary by category and year."
            )

        # Courses
        if any(word in query for word in ["course", "branch", "program", "department"]):
            response_parts.append(
                "UG: B.Tech in CSE, ECE, EEE, AI & DS\n"
                "PG: M.Tech in Embedded Systems, CSE\n"
                "Diploma and certification programs are also available."
            )

        # Placements
        if "placement" in query or "companies" in query:
            response_parts.append(
                "Top recruiters: Infosys, Wipro, TCS, HCL, Tech Mahindra, Cognizant, Capgemini, etc."
            )

        # Events
        if "event" in query or "fest" in query or "celebration" in query:
            response_parts.append("Events like Tech Fest, Cultural Fest 'VIBES', and Women's Day are celebrated.")

        # Contact
        if "contact" in query or "phone" in query or "email" in query:
            response_parts.append(
                "Phone: +91 863 229 3336\nEmail: vignannirula@vnits.ac.in\nWebsite: www.vignannirula.org"
            )

        # Timetable
        if "timetable" in query or "schedule" in query:
            branch_name = None
            for b in Branch.objects.all():
                if b.name.lower() in query:
                    branch_name = b.name
                    break
            if branch_name:
                branch = Branch.objects.get(name__iexact=branch_name)
                timetables = Timetable.objects.filter(branch=branch)
                if timetables.exists():
                    temp = f"Timetable for {branch.name}:\n"
                    for t in timetables:
                        temp += f"{t.day} - {t.time}: {t.subject}\n"
                    response_parts.append(temp)
                else:
                    response_parts.append(f"No timetable found for {branch_name}.")
            else:
                response_parts.append("Please mention a valid branch (e.g., 'Show timetable for CSE').")

        # Room / Block
        if "room" in query or "block" in query:
            if "cse" in query:
                response_parts.append("CSE: Hanuman Block First Floor, Room 801-805.")
            elif "ece" in query:
                response_parts.append("ECE: Hanuman Block Second Floor, Room 901-905.")
            elif "eee" in query:
                response_parts.append("EEE: Nirula Block, Room 601-602.")
            elif "it" in query:
                response_parts.append("IT: Hanuman Block, Room 906-910.")
            elif "ai" in query or "ds" in query:
                response_parts.append("AI & DS: Block A, Room 115.")
            elif "bs&h" in query:
                response_parts.append("BS&H: Block E, Room 201.")
            else:
                response_parts.append("Please specify the department to get room number.")

        # Fallback
        if not response_parts:
            response_parts.append("Sorry, I didn’t understand that. Try asking about students, college info, HODs, etc.")

        return JsonResponse({'response': "\n".join(response_parts)})

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
