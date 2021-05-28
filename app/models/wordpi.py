from sqlalchemy import Column, Integer, String, Boolean

from app.database import Base


class Wordpi(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True, nullable=False)
    is_beast = Column(Boolean, default=True)  # 是否生词，默认是生词
    tick = Column(Integer, default=0)  # 计数
    base_trans = Column(String(120))  # 基本含义
    trans = Column(String)  # 不同词性翻译
    en_trans = Column(String)  # 英文翻译
    examples = Column(String)  # 例句

    def __repr__(self):
        return f"<Wordpi {self.name}>"
