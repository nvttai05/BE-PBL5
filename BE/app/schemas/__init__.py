from .detection import DetectionResponse, DetectionItem
from .speak import SpeakRequest, SpeakResponse
from .history import HistoryResponse, HistoryItem
from .quiz import QuizRequest, QuizResponse, QuizQuestion
from .common import ErrorResponse, StatusResponse

__all__ = [
    "DetectionResponse", "DetectionItem",
    "SpeakRequest", "SpeakResponse",
    "HistoryResponse", "HistoryItem",
    "QuizRequest", "QuizResponse", "QuizQuestion",
    "ErrorResponse", "StatusResponse"
]
