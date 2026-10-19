import pytest
from pydantic import ValidationError
from app.schemas.engagement import ReviewCreate, MessageCreate, RecommendationRequest, TravelAssistantRequest, SupportChatRequest


def test_review_rating_range():
    assert ReviewCreate(booking_id=1, rating=5).rating == 5
    with pytest.raises(ValidationError):
        ReviewCreate(booking_id=1, rating=6)


def test_message_must_not_be_blank():
    with pytest.raises(ValidationError):
        MessageCreate(content="   ")
    assert MessageCreate(content=" hello ").content == "hello"


def test_recommendation_limit_bounds():
    assert RecommendationRequest(limit=10).limit == 10
    with pytest.raises(ValidationError):
        RecommendationRequest(limit=100)


def test_travel_assistant_input_bounds():
    assert TravelAssistantRequest(destination="Pune", nights=2).nights == 2
    with pytest.raises(ValidationError):
        TravelAssistantRequest(destination="Pune", nights=0)


def test_support_message_must_not_be_blank():
    with pytest.raises(ValidationError):
        SupportChatRequest(message=" ")
