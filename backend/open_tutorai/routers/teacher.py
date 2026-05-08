"""
Teacher router — assignments, submissions, and student listing.
All endpoints require teacher or admin role.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

import open_webui.utils.auth as auth
from open_webui.internal.db import get_db
from open_webui.models.users import Users

from open_tutorai.models.database import Assignment, Submission

router = APIRouter()


# ─────────────────────────────────────────
# Auth helpers
# ─────────────────────────────────────────

def get_teacher_or_admin(user=Depends(auth.get_verified_user)):
    if user.role not in {"teacher", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only teachers and admins can access this.")
    return user


# ─────────────────────────────────────────
# Pydantic schemas
# ─────────────────────────────────────────

class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    course: Optional[str] = None
    course_id: Optional[str] = None
    course_color: Optional[str] = "from-indigo-500 to-indigo-600"
    due_date: str           # YYYY-MM-DD
    due_time: Optional[str] = "23:59"
    points: Optional[int] = 100


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    course: Optional[str] = None
    course_id: Optional[str] = None
    course_color: Optional[str] = None
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    points: Optional[int] = None
    status: Optional[str] = None


class AssignmentResponse(BaseModel):
    id: str
    teacher_id: str
    title: str
    description: Optional[str]
    course: Optional[str]
    course_id: Optional[str]
    course_color: Optional[str]
    due_date: str
    due_time: str
    points: int
    status: str
    submission_count: int = 0
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    assignment_id: str
    content: Optional[str] = None
    file_ids: Optional[List[str]] = None


class SubmissionGrade(BaseModel):
    grade: Optional[str] = None
    feedback: Optional[str] = None


class SubmissionResponse(BaseModel):
    id: str
    assignment_id: str
    student_id: str
    student_name: Optional[str]
    student_email: Optional[str]
    content: Optional[str]
    file_ids: Optional[List[str]]
    status: str
    grade: Optional[str]
    feedback: Optional[str]
    submitted_at: Optional[str]
    graded_at: Optional[str]

    class Config:
        from_attributes = True


class StudentResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    profile_image_url: Optional[str] = None
    last_active_at: Optional[int] = None
    created_at: Optional[int] = None


# ─────────────────────────────────────────
# Student listing
# ─────────────────────────────────────────

@router.get("/students", response_model=List[StudentResponse])
async def get_students(user=Depends(get_teacher_or_admin)):
    """Returns all users with role 'user' (students)."""
    try:
        return [
            StudentResponse(
                id=u.id, name=u.name, email=u.email, role=u.role,
                profile_image_url=getattr(u, "profile_image_url", None),
                last_active_at=getattr(u, "last_active_at", None),
                created_at=getattr(u, "created_at", None),
            )
            for u in Users.get_users()
            if u.role == "user"
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# Assignments — CRUD
# ─────────────────────────────────────────

def _assignment_to_response(a: Assignment, db: Session) -> AssignmentResponse:
    sub_count = db.query(Submission).filter(Submission.assignment_id == a.id).count()
    return AssignmentResponse(
        id=a.id,
        teacher_id=a.teacher_id,
        title=a.title,
        description=a.description,
        course=a.course,
        course_id=a.course_id,
        course_color=a.course_color or "from-indigo-500 to-indigo-600",
        due_date=a.due_date,
        due_time=a.due_time or "23:59",
        points=a.points or 100,
        status=a.status or "active",
        submission_count=sub_count,
        created_at=a.created_at.isoformat() if a.created_at else None,
        updated_at=a.updated_at.isoformat() if a.updated_at else None,
    )


@router.get("/assignments", response_model=List[AssignmentResponse])
async def list_assignments(user=Depends(get_teacher_or_admin), db: Session = Depends(get_db)):
    """List all assignments created by the current teacher."""
    assignments = db.query(Assignment).filter(Assignment.teacher_id == user.id).order_by(Assignment.created_at.desc()).all()
    return [_assignment_to_response(a, db) for a in assignments]


@router.post("/assignments", response_model=AssignmentResponse, status_code=201)
async def create_assignment(form: AssignmentCreate, user=Depends(get_teacher_or_admin), db: Session = Depends(get_db)):
    """Create a new assignment."""
    a = Assignment(
        id=str(uuid.uuid4()),
        teacher_id=user.id,
        title=form.title,
        description=form.description,
        course=form.course,
        course_id=form.course_id,
        course_color=form.course_color,
        due_date=form.due_date,
        due_time=form.due_time or "23:59",
        points=form.points or 100,
        status="active",
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return _assignment_to_response(a, db)


@router.put("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(assignment_id: str, form: AssignmentUpdate, user=Depends(get_teacher_or_admin), db: Session = Depends(get_db)):
    a = db.query(Assignment).filter(Assignment.id == assignment_id, Assignment.teacher_id == user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    for field, value in form.dict(exclude_unset=True).items():
        setattr(a, field, value)
    a.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(a)
    return _assignment_to_response(a, db)


@router.delete("/assignments/{assignment_id}")
async def delete_assignment(assignment_id: str, user=Depends(get_teacher_or_admin), db: Session = Depends(get_db)):
    a = db.query(Assignment).filter(Assignment.id == assignment_id, Assignment.teacher_id == user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(a)
    db.commit()
    return {"message": "Assignment deleted"}


# ─────────────────────────────────────────
# Submissions — teacher views
# ─────────────────────────────────────────

def _sub_to_response(s: Submission) -> SubmissionResponse:
    return SubmissionResponse(
        id=s.id,
        assignment_id=s.assignment_id,
        student_id=s.student_id,
        student_name=s.student_name,
        student_email=s.student_email,
        content=s.content,
        file_ids=s.file_ids or [],
        status=s.status,
        grade=s.grade,
        feedback=s.feedback,
        submitted_at=s.submitted_at.isoformat() if s.submitted_at else None,
        graded_at=s.graded_at.isoformat() if s.graded_at else None,
    )


@router.get("/assignments/{assignment_id}/submissions", response_model=List[SubmissionResponse])
async def get_submissions(assignment_id: str, user=Depends(get_teacher_or_admin), db: Session = Depends(get_db)):
    """Get all submissions for an assignment (teacher only)."""
    a = db.query(Assignment).filter(Assignment.id == assignment_id, Assignment.teacher_id == user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    subs = db.query(Submission).filter(Submission.assignment_id == assignment_id).order_by(Submission.submitted_at.desc()).all()
    return [_sub_to_response(s) for s in subs]


@router.put("/submissions/{submission_id}/grade", response_model=SubmissionResponse)
async def grade_submission(submission_id: str, form: SubmissionGrade, user=Depends(get_teacher_or_admin), db: Session = Depends(get_db)):
    """Grade a submission and optionally leave feedback."""
    s = db.query(Submission).filter(Submission.id == submission_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")
    # Verify teacher owns the assignment
    a = db.query(Assignment).filter(Assignment.id == s.assignment_id, Assignment.teacher_id == user.id).first()
    if not a:
        raise HTTPException(status_code=403, detail="Not your assignment")
    s.grade = form.grade
    s.feedback = form.feedback
    s.status = "graded"
    s.graded_at = datetime.utcnow()
    db.commit()
    db.refresh(s)
    return _sub_to_response(s)


# ─────────────────────────────────────────
# Submissions — student submits
# ─────────────────────────────────────────

@router.post("/submissions", response_model=SubmissionResponse, status_code=201)
async def create_submission(form: SubmissionCreate, user=Depends(auth.get_verified_user), db: Session = Depends(get_db)):
    """Student submits work for an assignment."""
    a = db.query(Assignment).filter(Assignment.id == form.assignment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Check for duplicate submission
    existing = db.query(Submission).filter(
        Submission.assignment_id == form.assignment_id,
        Submission.student_id == user.id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You already submitted this assignment")

    # Determine if late
    try:
        due = datetime.strptime(f"{a.due_date}T{a.due_time}", "%Y-%m-%dT%H:%M")
        sub_status = "late" if datetime.utcnow() > due else "submitted"
    except Exception:
        sub_status = "submitted"

    s = Submission(
        id=str(uuid.uuid4()),
        assignment_id=form.assignment_id,
        student_id=user.id,
        student_name=user.name,
        student_email=user.email,
        content=form.content,
        file_ids=form.file_ids or [],
        status=sub_status,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return _sub_to_response(s)


@router.get("/my-submissions", response_model=List[SubmissionResponse])
async def get_my_submissions(user=Depends(auth.get_verified_user), db: Session = Depends(get_db)):
    """Student views their own submissions."""
    subs = db.query(Submission).filter(Submission.student_id == user.id).all()
    return [_sub_to_response(s) for s in subs]
