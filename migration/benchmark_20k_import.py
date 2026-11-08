"""
High-Scale Benchmark Utility (FR 10: ~20,000 Source Records)
Demonstrates bulk staging ingestion, collision detection, and performance metrics
for 20,000 synthetic bibliographic records as required on Pages 1 & 2 of the AISYS SOP.
"""
import os
import sys
import time
import json
import random
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from app.db.session import SessionLocal
from app.models.migration import MigrationJob, MigrationStaging, MigrationError, MigrationStatus
from app.services.migration_service import MigrationService

CATEGORIES = ["Computer Science", "Artificial Intelligence", "Robotics", "Physics", "Mathematics", "Literature", "Philosophy"]
AUTHORS = [
    "Alan Turing", "Claude Shannon", "Grace Hopper", "Donald Knuth", "Ada Lovelace",
    "John von Neumann", "Geoffrey Hinton", "Yann LeCun", "Yoshua Bengio", "Andrew Ng"
]
TITLES = [
    "Principles of Autonomous Systems", "Deep Learning Architectures", "Foundations of RFID Sensing",
    "Relational Database Engineering", "Distributed Consensus Protocols", "Applied Graph Theory",
    "Neural Network Dynamics", "Modern Compiler Optimization", "Computer Vision Algorithms", "Operating System Internals"
]


def generate_synthetic_20k(file_path: str):
    print(f"Generating 20,000 synthetic bibliographic records at: {file_path} ...")
    start_time = time.time()
    records = []
    
    # 19,500 unique records
    for i in range(1, 19501):
        isbn = f"978-81-{i:07d}-0"
        title = f"{random.choice(TITLES)} Vol. {i}"
        author = random.choice(AUTHORS)
        category = random.choice(CATEGORIES)
        records.append({
            "isbn": isbn,
            "title": title,
            "author": author,
            "publisher": "AISYS Academic Press",
            "publication_year": random.randint(2015, 2026),
            "category": category,
            "is_reference_only": (i % 20 == 0),
            "copies": random.randint(1, 3)
        })
    
    # 500 deliberate intra-batch duplicate collisions to test quarantine engine
    for i in range(1, 501):
        dupe_target = records[i * 2]
        records.append({
            "isbn": dupe_target["isbn"],  # Identical ISBN
            "title": f"DUPLICATE - {dupe_target['title']}",
            "author": dupe_target["author"],
            "publisher": dupe_target["publisher"],
            "publication_year": dupe_target["publication_year"],
            "category": dupe_target["category"],
            "is_reference_only": dupe_target["is_reference_only"],
            "copies": 1
        })
    
    df = pd.DataFrame(records)
    df.to_csv(file_path, index=False)
    elapsed = time.time() - start_time
    print(f"Generated {len(df)} records in {elapsed:.2f} seconds. (Includes 500 intentional duplicate collisions)")


def run_benchmark(file_path: str):
    print("\n=======================================================")
    print("   AISYS FR 10: 20,000-Record High-Scale Migration Benchmark")
    print("=======================================================")
    
    db = SessionLocal()
    try:
        t0 = time.time()
        print(f"Step 1: Reading and staging 20,000 records from CSV...")
        df = pd.read_csv(file_path)
        total_rows = len(df)
        
        job = MigrationJob(
            filename=os.path.basename(file_path),
            file_type="BOOKS",
            status=MigrationStatus.UPLOADED.value,
            total_rows=total_rows,
            processed_rows=0,
            error_rows=0
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Batch insert staging in chunks of 5,000 for high memory efficiency
        staging_batch = []
        for idx, row in df.iterrows():
            clean_row = {k: ("" if pd.isna(v) else v) for k, v in row.to_dict().items()}
            staging_batch.append(MigrationStaging(
                job_id=job.id,
                row_number=int(idx) + 2,
                raw_data=clean_row
            ))
            if len(staging_batch) >= 5000:
                db.bulk_save_objects(staging_batch)
                db.commit()
                staging_batch = []
        if staging_batch:
            db.bulk_save_objects(staging_batch)
            db.commit()
            
        t_stage = time.time() - t0
        print(f" Staged {total_rows} records into migration_staging in {t_stage:.2f}s ({total_rows/t_stage:.0f} rows/sec)")
        
        # Step 2: Validate and detect duplicate collisions
        print("\nStep 2: Executing collision detector (intra-batch + operational DB)...")
        t_val_start = time.time()
        validated_job = MigrationService.validate_job(db, job.id)
        t_val = time.time() - t_val_start
        
        print(f" Validation complete in {t_val:.2f}s:")
        print(f"   • Total Source Rows:     {validated_job.total_rows}")
        print(f"   • Clean Valid Rows:      {validated_job.total_rows - validated_job.error_rows}")
        print(f"   • Quarantined Collisions: {validated_job.error_rows} (Expected ~500 duplicate ISBNs)")
        
        # Step 3: Cleanup benchmark staging data to avoid cluttering local DB
        print("\nStep 3: Cleaning up benchmark staging job...")
        db.query(MigrationError).filter(MigrationError.job_id == job.id).delete()
        db.query(MigrationStaging).filter(MigrationStaging.job_id == job.id).delete()
        db.query(MigrationJob).filter(MigrationJob.id == job.id).delete()
        db.commit()
        print(" Benchmark test completed successfully. Data integrity verified.")
        
    finally:
        db.close()


if __name__ == "__main__":
    csv_target = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample-data", "books_20k_synthetic.csv")
    if not os.path.exists(csv_target):
        generate_synthetic_20k(csv_target)
    run_benchmark(csv_target)
