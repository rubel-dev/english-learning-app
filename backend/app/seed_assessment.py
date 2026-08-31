from app.db.session import SessionLocal
from backend.app.modules.assessment.models.assessment import Assessment
from app.seed.assessment_data import assessment_data


db = SessionLocal()

try:
    assessment = Assessment(
        content=assessment_data
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    print("Assessment inserted successfully!")
    print("Assessment ID:", assessment.id)

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()