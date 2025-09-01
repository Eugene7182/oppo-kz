from sqlalchemy import Column, Integer, ForeignKey, Numeric
from app.db.base_class import Base

class BonusOverachievementRule(Base):
    __tablename__ = "bonus_overachievement_rules"
    id = Column(Integer, primary_key=True, index=True)
    bonus_grid_id = Column(Integer, ForeignKey("bonus_grids.id", ondelete="CASCADE"), index=True, nullable=False)
    threshold_percent = Column(Integer, nullable=False)   # 110 => 110% плана
    bonus_amount = Column(Numeric(12, 2), nullable=False, default=0)
