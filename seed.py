from datetime import datetime, date, timedelta
import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.core.security import hash_password


def seed_database():
    print("Starting Nexora API database seed...")

    # Drop and recreate all tables for a clean slate
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 1. Seed Users (8 users)
        print("  - Creating Users...")
        default_password_hash = hash_password("Pass123456")

        users_data = [
            {"name": "Sai Krishna", "email": "sai@example.com"},
            {"name": "Alex Morgan", "email": "alex@example.com"},
            {"name": "Priyanshu Sharma", "email": "priyanshu@example.com"},
            {"name": "Sarah Jenkins", "email": "sarah@example.com"},
            {"name": "David Chen", "email": "david@example.com"},
            {"name": "Ananya Patel", "email": "ananya@example.com"},
            {"name": "Liam Vance", "email": "liam@example.com"},
            {"name": "Elena Rostova", "email": "elena@example.com"}
        ]

        users = []
        for u in users_data:
            user = User(
                name=u["name"],
                email=u["email"],
                password_hash=default_password_hash,
                created_at=datetime.utcnow() - timedelta(days=30),
                updated_at=datetime.utcnow() - timedelta(days=30)
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        for u in users:
            db.refresh(u)

        print(f"    [OK] Created {len(users)} users.")

        # 2. Seed Projects (5 projects)
        print("  - Creating Projects...")
        projects_data = [
            {
                "name": "Innovation Hacks Platform",
                "description": "Central hackathon portal for submissions, evaluation, and leaderboard management.",
                "owner_id": users[0].id
            },
            {
                "name": "AI Resume Analyzer",
                "description": "An AI-powered candidate resume parser, skill extractor, and ATS matching backend.",
                "owner_id": users[1].id
            },
            {
                "name": "Campus Connect",
                "description": "University student collaboration platform for events, notes sharing, and study groups.",
                "owner_id": users[2].id
            },
            {
                "name": "E-Commerce Dashboard",
                "description": "Real-time sales tracking analytics, inventory management, and store management REST API.",
                "owner_id": users[3].id
            },
            {
                "name": "Team Productivity Hub",
                "description": "Agile kanban board backend for sprint planning, task execution, and team workflow management.",
                "owner_id": users[4].id
            }
        ]

        projects = []
        for p in projects_data:
            proj = Project(
                name=p["name"],
                description=p["description"],
                owner_id=p["owner_id"],
                created_at=datetime.utcnow() - timedelta(days=20),
                updated_at=datetime.utcnow() - timedelta(days=20)
            )
            db.add(proj)
            projects.append(proj)

        db.commit()
        for p in projects:
            db.refresh(p)

        print(f"    [OK] Created {len(projects)} projects.")

        # 3. Seed Tasks (26 tasks)
        print("  - Creating Tasks...")
        today = date.today()

        tasks_data = [
            # Project 1: Innovation Hacks Platform (5 tasks)
            {
                "title": "Design authentication flow",
                "description": "Implement OAuth2 and JWT token handler for student signups",
                "project_id": projects[0].id,
                "assignee_id": users[0].id,
                "status": "done",
                "priority": "high",
                "due_date": today - timedelta(days=5)
            },
            {
                "title": "Build hackathon submission endpoint",
                "description": "API endpoint for project links, media uploads, and team details",
                "project_id": projects[0].id,
                "assignee_id": users[2].id,
                "status": "in-progress",
                "priority": "high",
                "due_date": today + timedelta(days=3)
            },
            {
                "title": "Create leaderboard scoring pipeline",
                "description": "Calculate judge rubric averages and sort entries dynamically",
                "project_id": projects[0].id,
                "assignee_id": users[4].id,
                "status": "todo",
                "priority": "medium",
                "due_date": today + timedelta(days=10)
            },
            {
                "title": "Setup database migrations",
                "description": "Configure Alembic migrations for production PostgreSQL deployment",
                "project_id": projects[0].id,
                "assignee_id": users[0].id,
                "status": "done",
                "priority": "medium",
                "due_date": today - timedelta(days=2)
            },
            {
                "title": "Write API integration tests",
                "description": "Achieve >85% test coverage for submission and scoring routers",
                "project_id": projects[0].id,
                "assignee_id": users[5].id,
                "status": "todo",
                "priority": "low",
                "due_date": today + timedelta(days=14)
            },

            # Project 2: AI Resume Analyzer (5 tasks)
            {
                "title": "Implement resume parsing pipeline",
                "description": "Extract raw text from PDF and DOCX uploads using PyMuPDF",
                "project_id": projects[1].id,
                "assignee_id": users[1].id,
                "status": "in-progress",
                "priority": "high",
                "due_date": today + timedelta(days=2)
            },
            {
                "title": "Extract candidate skills via NLP",
                "description": "Integrate SpaCy entity recognizer to extract technical skills",
                "project_id": projects[1].id,
                "assignee_id": users[6].id,
                "status": "todo",
                "priority": "high",
                "due_date": today + timedelta(days=7)
            },
            {
                "title": "Calculate job matching score",
                "description": "Vector cosine similarity matching between resume embeddings and job desc",
                "project_id": projects[1].id,
                "assignee_id": users[1].id,
                "status": "todo",
                "priority": "medium",
                "due_date": today + timedelta(days=12)
            },
            {
                "title": "Format ATS scorecard response",
                "description": "Return structured JSON recommendations for resume improvements",
                "project_id": projects[1].id,
                "assignee_id": users[3].id,
                "status": "done",
                "priority": "low",
                "due_date": today - timedelta(days=1)
            },
            {
                "title": "Optimize SpaCy pipeline performance",
                "description": "Cache model loadings in memory for fast inference response times",
                "project_id": projects[1].id,
                "assignee_id": users[1].id,
                "status": "done",
                "priority": "medium",
                "due_date": today - timedelta(days=4)
            },

            # Project 3: Campus Connect (5 tasks)
            {
                "title": "Build student profile API",
                "description": "CRUD endpoints for major, graduation year, bio, and social links",
                "project_id": projects[2].id,
                "assignee_id": users[2].id,
                "status": "done",
                "priority": "medium",
                "due_date": today - timedelta(days=6)
            },
            {
                "title": "Implement campus event creation",
                "description": "Allow club leads to publish events with RSVPs",
                "project_id": projects[2].id,
                "assignee_id": users[7].id,
                "status": "in-progress",
                "priority": "high",
                "due_date": today + timedelta(days=4)
            },
            {
                "title": "Create notes repository search",
                "description": "ElasticSearch integration for PDF lecture notes",
                "project_id": projects[2].id,
                "assignee_id": users[2].id,
                "status": "todo",
                "priority": "medium",
                "due_date": today + timedelta(days=15)
            },
            {
                "title": "Setup push notification service",
                "description": "WebPush notifications for study group chat updates",
                "project_id": projects[2].id,
                "assignee_id": None,
                "status": "todo",
                "priority": "low",
                "due_date": today + timedelta(days=20)
            },
            {
                "title": "Build study room booking API",
                "description": "Calendar availability slots for library room reservations",
                "project_id": projects[2].id,
                "assignee_id": users[4].id,
                "status": "in-progress",
                "priority": "medium",
                "due_date": today + timedelta(days=8)
            },

            # Project 4: E-Commerce Dashboard (5 tasks)
            {
                "title": "Build inventory analytics API",
                "description": "Aggregate stock levels, low-stock warnings, and reorder points",
                "project_id": projects[3].id,
                "assignee_id": users[3].id,
                "status": "done",
                "priority": "high",
                "due_date": today - timedelta(days=7)
            },
            {
                "title": "Create revenue report endpoints",
                "description": "Monthly and daily sales summary with filtering by category",
                "project_id": projects[3].id,
                "assignee_id": users[5].id,
                "status": "in-progress",
                "priority": "high",
                "due_date": today + timedelta(days=1)
            },
            {
                "title": "Implement order status webhook handler",
                "description": "Stripe/PayPal payment status update listener",
                "project_id": projects[3].id,
                "assignee_id": users[3].id,
                "status": "done",
                "priority": "medium",
                "due_date": today - timedelta(days=3)
            },
            {
                "title": "Customer order history query",
                "description": "Optimized pagination query for user order lists",
                "project_id": projects[3].id,
                "assignee_id": users[6].id,
                "status": "in-progress",
                "priority": "low",
                "due_date": today + timedelta(days=5)
            },
            {
                "title": "Export analytics to CSV/XLSX",
                "description": "Background worker task to stream large sales reports",
                "project_id": projects[3].id,
                "assignee_id": None,
                "status": "todo",
                "priority": "low",
                "due_date": today + timedelta(days=18)
            },

            # Project 5: Team Productivity Hub (6 tasks)
            {
                "title": "Create kanban task column move API",
                "description": "Update task status and order index in single atomic operation",
                "project_id": projects[4].id,
                "assignee_id": users[4].id,
                "status": "done",
                "priority": "high",
                "due_date": today - timedelta(days=10)
            },
            {
                "title": "Implement sprint velocity tracker",
                "description": "Calculate story point completion rates across 2-week sprints",
                "project_id": projects[4].id,
                "assignee_id": users[7].id,
                "status": "in-progress",
                "priority": "medium",
                "due_date": today + timedelta(days=6)
            },
            {
                "title": "Create dashboard analytics API",
                "description": "Aggregate summary metrics for tasks by status and priority",
                "project_id": projects[4].id,
                "assignee_id": users[0].id,
                "status": "done",
                "priority": "high",
                "due_date": today - timedelta(days=1)
            },
            {
                "title": "Build task comment thread API",
                "description": "Endpoints to add, update, and retrieve activity comments on tasks",
                "project_id": projects[4].id,
                "assignee_id": users[1].id,
                "status": "todo",
                "priority": "medium",
                "due_date": today + timedelta(days=11)
            },
            {
                "title": "Configure Redis caching for dashboard",
                "description": "Cache heavy summary counts for 60 seconds",
                "project_id": projects[4].id,
                "assignee_id": users[4].id,
                "status": "todo",
                "priority": "low",
                "due_date": today + timedelta(days=25)
            },
            {
                "title": "Implement team role access control",
                "description": "Enforce Admin, Member, and Viewer permissions on projects",
                "project_id": projects[4].id,
                "assignee_id": users[3].id,
                "status": "in-progress",
                "priority": "high",
                "due_date": today + timedelta(days=4)
            }
        ]

        tasks = []
        for t in tasks_data:
            task = Task(
                title=t["title"],
                description=t["description"],
                project_id=t["project_id"],
                assignee_id=t["assignee_id"],
                status=t["status"],
                priority=t["priority"],
                due_date=t["due_date"],
                created_at=datetime.utcnow() - timedelta(days=15),
                updated_at=datetime.utcnow() - timedelta(days=5)
            )
            db.add(task)
            tasks.append(task)

        db.commit()

        print(f"    [OK] Created {len(tasks)} tasks.")
        print("Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
