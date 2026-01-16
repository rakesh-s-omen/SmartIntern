# SmartIntern Progress Monitoring System

## Overview
This Django-based internship management system now includes comprehensive progress monitoring features with support for Arts & Science internships.

## Key Features Added

### 1. **Progress Proof Tracking**
- Students can upload proof of their internship activities (PDFs, images, videos)
- Faculty can verify and review submitted proofs
- Track different types of proof: work samples, attendance, project milestones, task completion, presentations

### 2. **Expanded Departments**
The system now supports Arts & Science departments:
- **Arts & Humanities:** English Literature, History, Psychology, Sociology, Visual Arts, Music, Theatre Arts
- **Sciences:** Physics, Chemistry, Biology, Mathematics
- **Economics**

### 3. **Arts & Science Internship Domains**
Sample data includes realistic internships for non-engineering fields:
- Content Writing, Creative Writing, Journalism, Publishing
- Museum Curation, Art Gallery Management, Heritage Conservation
- Theater Production, Music Production, Film Making
- Social Work, Community Development, NGO Operations
- Laboratory Research, Field Research, Environmental Studies
- And many more...

### 4. **Organizations**
Sample data includes diverse organizations:
- UNESCO, British Museum, National Geographic, BBC
- WHO, NASA, ISRO, CERN
- NGOs: UNICEF, Red Cross, Teach For India
- Media: Netflix, Spotify, Adobe Creative

## Database Structure

### New Model: ProgressProof
- **proof_type:** work_sample, attendance, project_milestone, task_completion, presentation, other
- **title:** Description of the proof
- **description:** Detailed information about the progress
- **proof_file:** Upload field for PDFs, images (JPG/PNG), videos (MP4/AVI/MOV), documents
- **verification_status:** pending, verified, rejected
- **faculty_remarks:** Feedback from faculty
- **verified_by:** Faculty who verified the proof
- **verification_date:** When it was verified

## Sample Data Statistics
- **4 Admins** across different departments
- **8 Faculty members** from Arts & Science departments
- **20 Students** from various Arts & Science backgrounds
- **50 Internship applications** in Arts & Science domains
- **157 Progress proofs** submitted by students
- **231 Weekly logs** tracking regular progress
- **17 Completion certificates**

## Login Credentials

### Admins
- admin1/admin123 (CSE)
- admin2/admin123 (English)
- admin3/admin123 (Psychology)
- admin4/admin123 (Physics)

### Faculty
- faculty1/faculty123 to faculty8/faculty123

### Students
- student1/student123 to student20/student123

## New URLs

### Student URLs
- `/progress-proof/submit/<application_id>/` - Submit new progress proof
- `/progress-proof/view/<application_id>/` - View all proofs for an internship

### Faculty URLs
- `/progress-proof/verify/<proof_id>/` - Verify a progress proof
- `/progress-monitoring/` - Progress monitoring dashboard
  - View all progress submissions
  - Identify low-activity internships (less than 3 proofs)
  - Recent submissions feed
  - Statistics overview

## File Upload Support
The system accepts the following file formats for progress proofs:
- **Documents:** PDF, DOC, DOCX
- **Images:** JPG, JPEG, PNG
- **Videos:** MP4, AVI, MOV

Files are stored in: `media/progress_proofs/`

## How to Use

### For Students:
1. Login with student credentials
2. Go to approved internship in dashboard
3. Click "Progress" button to view/submit progress proofs
4. Click "Submit New Proof" to upload evidence
5. Select proof type, add title, description, and upload file
6. Track verification status

### For Faculty:
1. Login with faculty credentials
2. Click "Progress Monitoring Dashboard" from main dashboard
3. View statistics and recent submissions
4. Click "Verify" on pending proofs to review
5. Add remarks and approve/reject proofs
6. Monitor low-activity internships requiring attention

### For Admins:
- Access all features across all departments
- View comprehensive analytics
- Monitor progress across the entire institution

## Monitoring Features

### Low Activity Alerts
The system automatically identifies internships with:
- Less than 3 progress proofs submitted
- Helps faculty intervene early
- Ensures students are actually participating

### Verification Workflow
1. Student submits proof with evidence file
2. Proof appears in faculty dashboard as "Pending"
3. Faculty reviews file and description
4. Faculty verifies or rejects with remarks
5. Student receives feedback

## Technical Details

### File Storage
- Location: `c:\Users\Rakes\smartintern_project\media\progress_proofs\`
- File validation handled by Django validators
- Supports multiple file formats

### Database
- SQLite database: `db.sqlite3`
- All progress proofs stored with metadata
- Linked to internship applications

## Running the Application

```bash
# Run development server
python manage.py runserver

# Access the application
http://127.0.0.1:8000/

# Admin panel
http://127.0.0.1:8000/admin/
```

## Next Steps
1. Test the progress proof submission workflow
2. Verify faculty can approve/reject proofs
3. Check the monitoring dashboard statistics
4. Upload actual sample files if needed
5. Customize proof types based on requirements
