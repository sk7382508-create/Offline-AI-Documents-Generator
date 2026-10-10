from typing import Optional
from pydantic import BaseModel


class Table(BaseModel):
    headers: list[str]
    rows: list[list[str]]


class Section(BaseModel):
    heading: str
    paragraphs: list[str] = []
    bullets: list[str] = []
    table: Optional[Table] = None


class Outline(BaseModel):
    title: str
    subtitle: str
    headings: list[str]


class Document(BaseModel):
    title: str
    subtitle: str
    sections: list[Section]
