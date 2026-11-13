# Medicine Reminder System

A modern, responsive healthcare management web application built with Django.

## Features

- **User Authentication:** Secure registration, login, and personalized settings.
- **Dashboard:** At-a-glance view of today's schedule, weekly adherence charts, and medicine metrics.
- **Medicine Management:** Full CRUD operations for medicines. Specify dosage, frequency, and custom reminders.
- **Smart Reminders:** Active polling system that triggers desktop browser notifications, email reminders, and optional SMS alerts when a medicine is due.
- **Calendar View:** A full month view of all scheduled medicines using FullCalendar.js.
- **Reporting:** Adherence charts and history logs for patient tracking.
- **Medication History Timeline:** View recent dose activity, status trends, and notes for each scheduled reminder.
- **Refill Intelligence:** Get proactive refill warnings and due-soon alerts before medicine stock runs out.
- **Caregiver Access:** Manage connected family members or caregivers and share medication status.
- **Smart Filters:** Search and filter medicines by low stock, refill urgency, or attention-needed status.
- **Voice Reminders:** Opt in on the dashboard to hear medicine names and dose times when reminders are due. The dashboard must remain open.
- **QR Identification:** Generate a personal QR code for each medicine and scan it to open its details. The scanner also recognizes supported sample medicine-ID QR codes and filters your medicines by name.
- **Private Prescriptions:** Upload PDF or image prescriptions (up to 10 MB) and download them through an authenticated, owner-checked endpoint.
- **Symptom Checker & Health Information:** Save private symptom assessments, browse a small source-cited symptom-overlap dataset, review separately configured urgent warning signs, and search FDA-submitted medicine labels for educational information.
- **Modern UI:** Built with Vanilla CSS, Bootstrap 5, FontAwesome, and Chart.js, featuring a clean healthcare-themed design and dark mode support.

## Tech Stack

- **Backend:** Django 6.0.7
- **Database:** SQLite
- **Frontend:** HTML, CSS (Custom & Bootstrap), Vanilla JavaScript, Chart.js, FullCalendar.js
- **Forms:** Django Crispy Forms (Bootstrap 5 pack)

## Setup Instructions

1. **Clone or Extract the Project**
   Navigate to the project root directory.

2. **Activate the Virtual Environment**
   ```bash
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   (If not already installed)
   ```bash
   pip install django djangorestframework pillow django-crispy-forms crispy-bootstrap5 reportlab openpyxl django-apscheduler qrcode twilio
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a Superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Enable SMS delivery (optional)**
   Set the following environment variables before starting the app to enable live Twilio SMS reminders:
   ```bash
   set TWILIO_ACCOUNT_SID=your_account_sid
   set TWILIO_AUTH_TOKEN=your_auth_token
   set TWILIO_PHONE_NUMBER=+15551234567
   ```

8. **Configure email reminders**
   Create a `.env` file in the project root (beside `manage.py`) with your SMTP account and provider's app password. For Gmail, use an app password rather than your regular account password:
   ```bash
   EMAIL_HOST_USER=your-address@gmail.com
   EMAIL_HOST_PASSWORD=your-gmail-app-password
   DEFAULT_FROM_EMAIL=your-address@gmail.com
   ```
   The app loads this file when Django starts. Restart Django after creating or changing it. The default SMTP server is Gmail on port 587 with TLS. To use another provider, also set `EMAIL_HOST`, `EMAIL_PORT`, and `EMAIL_USE_TLS`. Email reminders require an account email address and enabled email notifications in the user's settings. Keep `.env` private; it is excluded from version control.

9. **Apply the latest migrations**
   ```bash
   python manage.py migrate
   ```

   Prescription uploads are stored in the private `private_prescriptions/` directory, outside the public media URL. Do not configure your web server to expose this directory.

10. **Access the Application**
   Open your browser and navigate to `http://127.0.0.1:8000/`.

   Camera QR scanning requires HTTPS or localhost and camera permission. Voice reminders use the browser's speech synthesis and run only while the dashboard is open.

   The symptom checker is informational, not diagnostic. Its initial condition associations cite CDC symptom pages; urgent warnings are maintained separately in the admin. Medicine lookups query the public openFDA drug-label API and do not send symptom selections or assessment notes. Review the medical content with qualified clinicians before using this feature in a clinical or production setting.

## Architecture Details

- **Accounts App:** Handles custom User model, authentication, and emergency contacts.
- **Medicines App:** Core CRUD operations, Dashboard views, settings, and reports.
- **Reminders App:** Handles Reminder time slots and MedicineLogs for tracking adherence.
- **API App:** Endpoints for JS polling and notification fetching.
- **Symptoms App:** Source-cited symptom matching, private assessment history, emergency warnings, health-information pages, FDA label lookup, admin management, and authenticated REST endpoints under `/api/symptoms/`.

The symptom-checker pages are under `/symptoms/`: `/symptoms/` for the checker, `/symptoms/assessments/` for history, `/symptoms/health-information/` for condition information, and `/symptoms/medicine-information/` for FDA label lookup. Run `python manage.py migrate` after pulling changes to create the tables and load the cited starter dataset.

The authenticated REST endpoints are `GET /api/symptoms/symptoms/`, `GET`/`POST /api/symptoms/assessments/`, `GET /api/symptoms/assessments/<id>/`, `GET /api/symptoms/diseases/`, `GET /api/symptoms/diseases/<id>/`, and `GET /api/symptoms/medicines/?q=<name>`. Run `python manage.py test symptoms.tests medicines.tests` to validate the feature and medicine regressions.
