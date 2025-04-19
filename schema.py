from pydantic import BaseModel
from typing import List, Literal, Union


class FillBlank(BaseModel):
    id: int
    question: str
    options: List[str]
    answer: int


class TrueFalse(BaseModel):
    id: int
    question: str
    answer: bool


class MatchColumn(BaseModel):
    id: int
    columna: List[str]
    columnb: List[str]
    answer: List[int]


class Quiz(BaseModel):
    id: int
    question: str
    options: List[str]
    answer: int


class ShortAnswer(BaseModel):
    id: int
    question: str
    answer: str


class LongAnswer(BaseModel):
    id: int
    question: str
    answer: str


class QuestionSet(BaseModel):
    fill_blank: List[FillBlank]
    true_false: List[TrueFalse]
    match_column: List[MatchColumn]
    quiz: List[Quiz]
    short_answer: List[ShortAnswer]
    long_answer: List[LongAnswer]
