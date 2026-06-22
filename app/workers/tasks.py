from app.workers.celery_app import celery
from app.db.database import SessionLocal

from app.services.csv_service import (
    clean_csv
)

from app.services.anomaly_service import (
    detect_anomalies
)

from app.services.transaction_service import (
    save_transactions
)

from app.services.job_service import (
    get_job_by_id,
    update_job_status,
    update_row_counts
)
from app.services.llm_service import (
    enrich_categories
)
from app.services.summary_service import (
    generate_summary
)

from app.services.summary_service import (
    save_summary
)

@celery.task
def process_csv_job(job_id):

    db = SessionLocal()

    try:

        job = get_job_by_id(
            db,
            job_id
        )

        update_job_status(
            db,
            job,
            "PROCESSING"
        )

        file_path = job.file_path

        df, raw_count, clean_count = (
            clean_csv(file_path)
        )

        update_row_counts(
            db,
            job,
            raw_count,
            clean_count
        )

        df = detect_anomalies(
            df
        )

        try:


            df = enrich_categories(
                df
            )


        except Exception as e:


            print(
                f"LLM Failed: {e}"
            )

            df["llm_failed"] = True

            df["llm_raw_response"] = ""


        save_transactions(
            db,
            job.id,
            df
        )

        summary = (
            generate_summary(df)
        )

        save_summary(
            db,
            job.id,
            summary
        )
        print(
            f"Processing Job {job_id}"
        )

        update_job_status(
            db,
            job,
            "COMPLETED"
        )

        return True

    except Exception as e:

        update_job_status(
            db,
            job,
            "FAILED"
        )

        print(
            f"Job {job_id} failed: {e}"
        )

        raise

    finally:

        db.close()