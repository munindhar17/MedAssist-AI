from backend.ml.inference import predict_disease


def test_predict_disease_returns_top_three_predictions():
    predictions = predict_disease(["itching", "skin_rash"])

    assert isinstance(predictions, list)
    assert len(predictions) <= 3

    for prediction in predictions:
        assert "disease" in prediction
        assert "confidence" in prediction
        assert "final_score" in prediction
        assert prediction["final_score"] >= 0.3


def test_predict_disease_filters_low_confidence():
    predictions = predict_disease(["unknown symptom", "another unknown symptom"])

    assert isinstance(predictions, list)
    assert len(predictions) <= 3
    for prediction in predictions:
        assert prediction["final_score"] >= 0.3
