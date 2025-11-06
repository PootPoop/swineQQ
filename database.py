import sqlite3
import csv
from typing import Optional, List
from pydantic import BaseModel, field_validator
import pandas as pd
from pathlib import Path


class SwineReportData(BaseModel):
    """Pydantic model matching Snowflake table SWINE_ALERT"""

    UNIQUE_ID: Optional[str]
    START_DATE: Optional[str]
    END_DATE: Optional[str]
    OPERATION: Optional[str]
    GMF_ID: Optional[str]
    ZALO_GROUP_NAME: Optional[str]
    FARM_CODE: Optional[str]
    FARM_NAME: Optional[str]
    FARM_TYPE: Optional[str]
    REPORT_BARN_CODE: Optional[str]
    SYSTEM_BARN_CODE: Optional[str]
    BARN_NAME: Optional[str]
    BLOOD_TYPE: Optional[str]
    FLOCK_CODE: Optional[str]
    FLOCK_NAME: Optional[str]
    PIG_IN_WEIGHT: Optional[float]
    PIG_IN_WEEK_AGE: Optional[int]
    PIG_IN_DAY_AGE: Optional[int]
    START_RAISING_DATE: Optional[str]
    RAISING_TYPE: Optional[str]
    JINI_JOIN_DATE: Optional[str]
    CUMULATIVE_FI_BEFORE_JINI: Optional[float]
    FP_AH_MESSAGE_ID: Optional[str]
    REPORT_DATE: Optional[str]
    BEGIN_POP_TOTAL: Optional[int]
    PIGLET_IN: Optional[int]
    SALES_TRANSFER: Optional[int]
    DEATH_CULLING_TOTAL: Optional[int]
    RAISE_WEEK: Optional[int]
    RAISE_DAY: Optional[int]
    BEGIN_POP: Optional[int]
    FARM_SOURCE: Optional[str]
    FEED_INTAKE_ACTUAL: Optional[float]
    FEED_TYPE: Optional[str]
    FEED_INTAKE_STD: Optional[float]
    TIME_EMPTY_FEEDER: Optional[str]
    DC_HEAD: Optional[int]
    DC_BEGIN_POP: Optional[int]
    DC_PERCENT: Optional[float]
    YTD_HEAD: Optional[int]
    YTD_TOTAL: Optional[int]
    YTD_PERCENT: Optional[float]
    ESTIMATED_WEIGHT: Optional[float]
    CALCULATED_RAISING_WEEK: Optional[int]
    CALCULATED_RAISING_DAY: Optional[int]
    PARENT_BARN: Optional[str]
    MIN_INDOOR_TEMPERATURE: Optional[float]
    MAX_INDOOR_TEMPERATURE: Optional[float]
    MIN_OUTDOOR_TEMPERATURE: Optional[float]
    MAX_OUTDOOR_TEMPERATURE: Optional[float]
    PNEUMONIA_COUNT: Optional[int]
    PNEUMONIA_PERCENT: Optional[float]
    DIARRHEA_COUNT: Optional[int]
    DIARRHEA_PERCENT: Optional[float]
    SUDDEN_DEATH_COUNT: Optional[int]
    SUDDEN_DEATH_PERCENT: Optional[float]
    FEVER_COUNT: Optional[int]
    FEVER_PERCENT: Optional[float]
    CONVULSION_COUNT: Optional[int]
    CONVULSION_PERCENT: Optional[float]
    ARTHRITIS_COUNT: Optional[int]
    ARTHRITIS_PERCENT: Optional[float]
    PARALYSIS_COUNT: Optional[int]
    PARALYSIS_PERCENT: Optional[float]
    DAILY_BEGIN_POP: Optional[int]
    GRADE_B: Optional[str]
    PRRS: Optional[str]
    VACCINATION: Optional[str]
    EXTRACTED_VACCINES: Optional[str]  # SQLite doesn't support ARRAY
    VL_MESSAGE_ID: Optional[str]
    ACTUAL_ON_DATE: Optional[str]
    ACTUAL_VEHICLES_ENTERING: Optional[int]
    ACTUAL_PEOPLE_ENTERING: Optional[int]
    ACTUAL_FOOD_COMES: Optional[str]
    ACTUAL_SUPPLIES: Optional[str]
    PLAN_ON_DATE: Optional[str]
    PLAN_VEHICLES_ENTERING: Optional[int]
    PLAN_PEOPLE_ENTERING: Optional[int]
    PLAN_FOOD_COMES: Optional[str]
    PLAN_SUPPLIES: Optional[str]
    FC_MESSAGE_ID: Optional[str]
    R1_NST: Optional[str]
    R1_GATE_DISINFECTION_PIT: Optional[str]
    R1_INSECT_NET: Optional[str]
    R1_BRAN_WAREHOUSE: Optional[str]
    R1_LIME_CORRIDOR: Optional[str]
    R1_FLIES_DETECTED: Optional[str]
    R1_RATS_DETECTED: Optional[str]
    R1_SOLUTION_FOR_FAILED_ITEMS: Optional[str]
    R2_NST: Optional[str]
    R2_GATE_DISINFECTION_PIT: Optional[str]
    R2_INSECT_NET: Optional[str]
    R2_BRAN_WAREHOUSE: Optional[str]
    R2_LIME_CORRIDOR: Optional[str]
    R2_FLIES_DETECTED: Optional[str]
    R2_RATS_DETECTED: Optional[str]
    R2_SOLUTION_FOR_FAILED_ITEMS: Optional[str]
    PC_MESSAGE_ID: Optional[str]
    FLIES_MOSQUITOES_DETECTED: Optional[str]
    RATS_DETECTED: Optional[str]
    WILD_ANIMALS_DETECTED: Optional[str]
    SPRAYING_DISINFECTANT: Optional[str]
    SPRAYING_FLY_POISON: Optional[str]
    SPRINKLING_RAT_BAIT: Optional[str]
    REPORT_MESSAGE_ID: Optional[str]
    ESC_0_TEXT: Optional[str]
    ESC_1_TEXT: Optional[str]
    ESC_2_TEXT: Optional[str]
    ALERT_TOPIC: Optional[str]
    ALERT_TYPE: Optional[str]
    CONCLUDE: Optional[str]
    REASON: Optional[str]
    SOLUTION: Optional[str]
    SEQ_NUM: Optional[int]

    class Config:
        allow_population_by_field_name = True

    @field_validator('*', pre=True)
    def empty_str_to_none(cls, v):
        if v == '' or v == 'NULL':
            return None
        return v


class SwineDatabase:
    """SQLite database that mirrors the Snowflake schema for local testing"""

    def __init__(self, db_path: str = "swine_data.db"):
        self.db_path = str((Path(__file__).parent / "data" / db_path).absolute())
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS SWINE_ALERT (
                UNIQUE_ID TEXT,
                START_DATE TEXT,
                END_DATE TEXT,
                OPERATION TEXT,
                GMF_ID TEXT,
                ZALO_GROUP_NAME TEXT,
                FARM_CODE TEXT,
                FARM_NAME TEXT,
                FARM_TYPE TEXT,
                REPORT_BARN_CODE TEXT,
                SYSTEM_BARN_CODE TEXT,
                BARN_NAME TEXT,
                BLOOD_TYPE TEXT,
                FLOCK_CODE TEXT,
                FLOCK_NAME TEXT,
                PIG_IN_WEIGHT REAL,
                PIG_IN_WEEK_AGE INTEGER,
                PIG_IN_DAY_AGE INTEGER,
                START_RAISING_DATE TEXT,
                RAISING_TYPE TEXT,
                JINI_JOIN_DATE TEXT,
                CUMULATIVE_FI_BEFORE_JINI REAL,
                FP_AH_MESSAGE_ID TEXT,
                REPORT_DATE TEXT,
                BEGIN_POP_TOTAL INTEGER,
                PIGLET_IN INTEGER,
                SALES_TRANSFER INTEGER,
                DEATH_CULLING_TOTAL INTEGER,
                RAISE_WEEK INTEGER,
                RAISE_DAY INTEGER,
                BEGIN_POP INTEGER,
                FARM_SOURCE TEXT,
                FEED_INTAKE_ACTUAL REAL,
                FEED_TYPE TEXT,
                FEED_INTAKE_STD REAL,
                TIME_EMPTY_FEEDER TEXT,
                DC_HEAD INTEGER,
                DC_BEGIN_POP INTEGER,
                DC_PERCENT REAL,
                YTD_HEAD INTEGER,
                YTD_TOTAL INTEGER,
                YTD_PERCENT REAL,
                ESTIMATED_WEIGHT REAL,
                CALCULATED_RAISING_WEEK INTEGER,
                CALCULATED_RAISING_DAY INTEGER,
                PARENT_BARN TEXT,
                MIN_INDOOR_TEMPERATURE REAL,
                MAX_INDOOR_TEMPERATURE REAL,
                MIN_OUTDOOR_TEMPERATURE REAL,
                MAX_OUTDOOR_TEMPERATURE REAL,
                PNEUMONIA_COUNT INTEGER,
                PNEUMONIA_PERCENT REAL,
                DIARRHEA_COUNT INTEGER,
                DIARRHEA_PERCENT REAL,
                SUDDEN_DEATH_COUNT INTEGER,
                SUDDEN_DEATH_PERCENT REAL,
                FEVER_COUNT INTEGER,
                FEVER_PERCENT REAL,
                CONVULSION_COUNT INTEGER,
                CONVULSION_PERCENT REAL,
                ARTHRITIS_COUNT INTEGER,
                ARTHRITIS_PERCENT REAL,
                PARALYSIS_COUNT INTEGER,
                PARALYSIS_PERCENT REAL,
                DAILY_BEGIN_POP INTEGER,
                GRADE_B TEXT,
                PRRS TEXT,
                VACCINATION TEXT,
                EXTRACTED_VACCINES TEXT,
                VL_MESSAGE_ID TEXT,
                ACTUAL_ON_DATE TEXT,
                ACTUAL_VEHICLES_ENTERING INTEGER,
                ACTUAL_PEOPLE_ENTERING INTEGER,
                ACTUAL_FOOD_COMES TEXT,
                ACTUAL_SUPPLIES TEXT,
                PLAN_ON_DATE TEXT,
                PLAN_VEHICLES_ENTERING INTEGER,
                PLAN_PEOPLE_ENTERING INTEGER,
                PLAN_FOOD_COMES TEXT,
                PLAN_SUPPLIES TEXT,
                FC_MESSAGE_ID TEXT,
                R1_NST TEXT,
                R1_GATE_DISINFECTION_PIT TEXT,
                R1_INSECT_NET TEXT,
                R1_BRAN_WAREHOUSE TEXT,
                R1_LIME_CORRIDOR TEXT,
                R1_FLIES_DETECTED TEXT,
                R1_RATS_DETECTED TEXT,
                R1_SOLUTION_FOR_FAILED_ITEMS TEXT,
                R2_NST TEXT,
                R2_GATE_DISINFECTION_PIT TEXT,
                R2_INSECT_NET TEXT,
                R2_BRAN_WAREHOUSE TEXT,
                R2_LIME_CORRIDOR TEXT,
                R2_FLIES_DETECTED TEXT,
                R2_RATS_DETECTED TEXT,
                R2_SOLUTION_FOR_FAILED_ITEMS TEXT,
                PC_MESSAGE_ID TEXT,
                FLIES_MOSQUITOES_DETECTED TEXT,
                RATS_DETECTED TEXT,
                WILD_ANIMALS_DETECTED TEXT,
                SPRAYING_DISINFECTANT TEXT,
                SPRAYING_FLY_POISON TEXT,
                SPRINKLING_RAT_BAIT TEXT,
                REPORT_MESSAGE_ID TEXT,
                ESC_0_TEXT TEXT,
                ESC_1_TEXT TEXT,
                ESC_2_TEXT TEXT,
                ALERT_TOPIC TEXT,
                ALERT_TYPE TEXT,
                CONCLUDE TEXT,
                REASON TEXT,
                SOLUTION TEXT,
                SEQ_NUM INTEGER
            )
        ''')

        conn.commit()
        conn.close()

    def insert_records_batch(self, records: List[SwineReportData]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for record in records:
            data = record.dict()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = list(data.values())
            cursor.execute(f'INSERT INTO SWINE_ALERT ({columns}) VALUES ({placeholders})', values)

        conn.commit()
        conn.close()

    def query_records(self, query: str = None, params: tuple = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if query is None:
            query = "SELECT * FROM SWINE_ALERT"

        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        conn.close()
        return rows


def parse_csv_to_database(csv_file_path: str, db_path: str = "swine_data.db"):
    """Parse CSV file and insert into local SQLite version of Snowflake schema"""
    db = SwineDatabase(db_path)
    records = []

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    record = SwineReportData(**row)
                    records.append(record)
                except Exception as e:
                    print(f"Row skipped due to error: {e}")
        print(f"Inserting {len(records)} records...")
        db.insert_records_batch(records)
        print("Insertion complete!")
        return db
    except FileNotFoundError:
        print(f"File not found: {csv_file_path}")
        return None
