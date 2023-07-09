from dataclasses import dataclass, field
from datetime import datetime,date
from typing import List

@dataclass
class Blog:
    _id: str
    title: str
    post: str
    created_at: date = field(default_factory=datetime.now().date)
    likes: int = 0
    shared: bool = False
    liked_by: List[str] = field(default_factory=list)


@dataclass
class User:
    _id: str
    email: str
    password: str
    written_blogs: List[str] = field(default_factory=list)
