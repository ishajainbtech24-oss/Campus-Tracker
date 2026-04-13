  Campus Tracker – Issue Reporting System

  Project Overview
Campus Tracker is a web-based platform designed to simplify and streamline the process of reporting and managing campus-related issues. It allows students to report problems and track their status, while administrators efficiently manage and resolve requests.

---

  Features

-  User Registration & Login (Secure Authentication)
-  Issue Reporting System (Category, Description, Location)
-  Student Dashboard (Track Requests)
-  Admin Dashboard (Manage Requests)
-  Request Status Tracking (Pending / In Progress / Resolved)
-  Notifications System
-  Analytics & Reports
-  Office Counter Availability Tracking
-  File Upload Support (Images)
-  Security Features (Password Hashing, Validation)

---

  User Roles

- **Student**  
  - Submit issues  
  - Track request status  

- **Admin**  
  - View all requests  
  - Update status  
  - Generate reports  

- **Staff**  
  - Assist in issue resolution  

---

 Tech Stack

 Frontend
- HTML
- CSS
- JavaScript

 Backend
- Python (Flask)

 Database
- MySQL

 DevOps
- Docker (Containerization)
- GitHub Actions (CI/CD Pipeline)

 Testing
- Pytest
- Manual Testing

---

 System Architecture

1. User logs in  
2. Submits request  
3. Data stored in database  
4. Admin processes request  
5. Status updated  
6. Notification sent  

---

 Database Design

The system uses **11 tables**:

- users
- students
- admins
- staff
- requests
- issue_requests
- service_requests
- notifications
- office_counters
- request_history
- reports

---

 Installation & Setup

 Clone the Repository
```bash
git clone https://github.com/your-repo/campus-tracker.git
cd campus-tracker
