"""
Local ML model for bail eligibility prediction.
Trained on synthetic data with fallback to rule-based system.
"""
import json
import logging
from typing import Dict, List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Try to import sklearn
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Using rule-based bail prediction.")


class BailEligibilityModel:
    """
    Machine learning model for predicting bail eligibility.
    Uses RandomForest when sklearn is available, falls back to rule-based system.
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.feature_names = None
        self.is_trained = False
        self.accuracy = 0.0
        self.precision = 0.0
        self.recall = 0.0
    
    def prepare_features(self, data: List[Dict]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Convert raw data to feature vectors for ML.
        
        Returns:
            X (features), y (labels), feature_names
        """
        
        feature_list = []
        labels = []
        
        feature_columns = [
            "age", "offence_severity", "prior_criminal_history",
            "employment_status", "monthly_income", "residential_stability",
            "years_in_current_city", "has_family_ties", "has_guarantor",
            "guarantor_income", "flight_risk", "is_repeat_offender",
            "days_between_arrest_and_trial", "health_conditions",
            "mental_health_issue", "credibility_score", "offence_category"
        ]
        
        self.feature_names = feature_columns
        
        for record in data:
            features = []
            
            # Numeric features
            features.append(record.get("age", 30))
            features.append(record.get("offence_severity", 3))
            
            # Categorical: prior_criminal_history
            prior_hist_map = {"none": 0, "minor": 1, "moderate": 2, "serious": 3}
            features.append(prior_hist_map.get(record.get("prior_criminal_history", "none"), 0))
            
            # Categorical: employment_status
            employment_map = {"employed": 3, "self_employed": 2, "student": 1, "unemployed": 0}
            features.append(employment_map.get(record.get("employment_status", "unemployed"), 0))
            
            # Numeric
            features.append(record.get("monthly_income", 25000) / 10000)  # Normalize
            
            # Categorical: residential_stability
            residential_map = {"owned": 3, "rented": 2, "with_family": 2, "migrant": 0, "homeless": 0}
            features.append(residential_map.get(record.get("residential_stability", "rented"), 1))
            
            # Numeric
            features.append(record.get("years_in_current_city", 5))
            
            # Boolean
            features.append(1 if record.get("has_family_ties", False) else 0)
            features.append(1 if record.get("has_guarantor", False) else 0)
            
            # Numeric
            features.append(record.get("guarantor_income", 0) / 10000)  # Normalize
            
            # Categorical: flight_risk
            flight_risk_map = {"low": 0, "medium": 1, "high": 2, "very_high": 3}
            features.append(flight_risk_map.get(record.get("flight_risk", "medium"), 1))
            
            # Boolean
            features.append(1 if record.get("is_repeat_offender", False) else 0)
            
            # Numeric
            features.append(record.get("days_between_arrest_and_trial", 100) / 50)  # Normalize
            
            # Boolean
            features.append(1 if record.get("health_conditions", False) else 0)
            features.append(1 if record.get("mental_health_issue", False) else 0)
            
            # Numeric
            features.append(record.get("credibility_score", 50) / 100)  # Normalize
            
            # Categorical: offence_category
            offence_map = {
                "theft": 2, "assault": 3, "fraud": 2, "traffic_violation": 1,
                "property_damage": 2, "petty_crime": 1, "white_collar": 2,
                "drug_related": 3, "violent_crime": 4, "cyber_crime": 1
            }
            features.append(offence_map.get(record.get("offence_category", "other"), 2))
            
            feature_list.append(features)
            labels.append(1 if record.get("bail_eligible", False) else 0)
        
        return np.array(feature_list), np.array(labels), feature_columns
    
    def train(self, dataset: List[Dict]) -> Dict:
        """
        Train the bail eligibility model.
        
        Args:
            dataset: List of training records
        
        Returns:
            Training metrics dictionary
        """
        
        if not SKLEARN_AVAILABLE:
            logger.warning("sklearn not available, skipping ML training")
            self.is_trained = False
            return {"error": "sklearn not available"}
        
        logger.info(f"Training bail model on {len(dataset)} records...")
        
        # Prepare features
        X, y, feature_names = self.prepare_features(dataset)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        self.accuracy = accuracy_score(y_test, y_pred)
        self.precision = precision_score(y_test, y_pred, zero_division=0)
        self.recall = recall_score(y_test, y_pred, zero_division=0)
        
        self.is_trained = True
        
        metrics = {
            "status": "trained",
            "training_records": len(dataset),
            "test_records": len(X_test),
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "model_type": "RandomForest",
            "features": len(feature_names),
        }
        
        logger.info(f"Model trained: Accuracy={self.accuracy:.4f}, Precision={self.precision:.4f}, Recall={self.recall:.4f}")
        return metrics
    
    def predict(self, case_data: Dict) -> Dict:
        """
        Predict bail eligibility for a case.
        
        Args:
            case_data: Case information dictionary
        
        Returns:
            Prediction with probability and reasoning
        """
        
        if not self.is_trained:
            # Fallback to rule-based prediction
            return self._rule_based_prediction(case_data)
        
        try:
            # Prepare single case as feature vector
            X, _, _ = self.prepare_features([case_data])
            X_scaled = self.scaler.transform(X)
            
            prediction = self.model.predict(X_scaled)[0]
            probability = self.model.predict_proba(X_scaled)[0]
            
            eligibility_confidence = float(probability[1])
            is_eligible = prediction == 1
            
            return {
                "case_id": case_data.get("case_id", "UNKNOWN"),
                "bail_eligible": is_eligible,
                "confidence": round(eligibility_confidence, 4),
                "recommendation": "Eligible for bail" if is_eligible else "Bail not recommended",
                "model_type": "ML_RandomForest",
                "reasoning": self._generate_reasoning(case_data, is_eligible, eligibility_confidence),
                "conditions": case_data.get("conditions_for_bail", []) if is_eligible else [],
                "recommended_bail_amount": case_data.get("recommended_bail_amount", 0) if is_eligible else 0,
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._rule_based_prediction(case_data)
    
    def _rule_based_prediction(self, case_data: Dict) -> Dict:
        """
        Rule-based bail eligibility prediction (fallback).
        """
        
        score = 100
        risks = []
        positives = []
        
        # Age factor
        age = case_data.get("age", 35)
        if age < 18 or age > 70:
            score -= 10
            risks.append("Extreme age")
        
        # Offence severity
        severity = case_data.get("offence_severity", 3)
        score -= severity * 10
        if severity >= 4:
            risks.append("Severe offence")
        
        # Criminal history
        prior_history = case_data.get("prior_criminal_history", "none")
        history_penalty = {"none": 0, "minor": 5, "moderate": 15, "serious": 30}
        score -= history_penalty.get(prior_history, 5)
        if prior_history != "none":
            risks.append(f"Prior {prior_history} criminal history")
        
        # Employment
        employment = case_data.get("employment_status", "unemployed")
        if employment != "unemployed":
            score += 10
            positives.append(f"Employed ({employment})")
        else:
            score -= 10
            risks.append("Unemployed")
        
        # Income
        income = case_data.get("monthly_income", 0)
        if income > 50000:
            score += 10
            positives.append("Stable income")
        elif income < 10000:
            score -= 10
        
        # Residential stability
        residential = case_data.get("residential_stability", "rented")
        if residential == "owned":
            score += 15
            positives.append("Owns residence")
        elif residential == "homeless":
            score -= 15
            risks.append("No fixed address")
        
        # Family ties
        if case_data.get("has_family_ties", False):
            score += 10
            positives.append("Strong family ties")
        
        # Guarantor
        if case_data.get("has_guarantor", False):
            score += 20
            positives.append("Has guarantor")
        
        # Flight risk
        flight_risk = case_data.get("flight_risk", "medium")
        flight_penalty = {"low": 0, "medium": 10, "high": 25, "very_high": 40}
        score -= flight_penalty.get(flight_risk, 10)
        if flight_risk != "low":
            risks.append(f"Flight risk: {flight_risk}")
        
        # Repeat offender
        if case_data.get("is_repeat_offender", False):
            score -= 30
            risks.append("Repeat offender")
        
        # Trial timeline
        days_to_trial = case_data.get("days_between_arrest_and_trial", 100)
        if days_to_trial < 30:
            score -= 10
            risks.append("Trial coming up soon")
        elif days_to_trial > 180:
            score += 5
        
        is_eligible = score >= 40
        confidence = min(0.95, max(0.5, (score + 50) / 250))  # Normalize score to confidence
        
        return {
            "case_id": case_data.get("case_id", "UNKNOWN"),
            "bail_eligible": is_eligible,
            "confidence": round(confidence, 4),
            "recommendation": "Eligible for bail" if is_eligible else "Bail not recommended",
            "model_type": "Rule_Based",
            "score": score,
            "risks": risks,
            "positives": positives,
            "reasoning": f"Score: {score}/100. Risks: {', '.join(risks) if risks else 'None'}. Positives: {', '.join(positives) if positives else 'None'}.",
            "conditions": case_data.get("conditions_for_bail", []) if is_eligible else [],
            "recommended_bail_amount": case_data.get("recommended_bail_amount", 0) if is_eligible else 0,
        }
    
    def _generate_reasoning(self, case_data: Dict, is_eligible: bool, confidence: float) -> str:
        """Generate human-readable reasoning for prediction."""
        
        factors = []
        
        if case_data.get("has_guarantor"):
            factors.append("strong guarantor support")
        
        if case_data.get("employment_status") != "unemployed":
            factors.append("stable employment")
        
        if case_data.get("offence_severity", 5) <= 2:
            factors.append("non-severe offence")
        
        if case_data.get("prior_criminal_history") == "none":
            factors.append("clean record")
        
        if case_data.get("flight_risk") == "low":
            factors.append("low flight risk")
        
        reasoning = f"{'Eligible' if is_eligible else 'Not eligible'} for bail (confidence: {confidence:.1%})"
        if factors:
            reasoning += f" based on {', '.join(factors)}."
        
        return reasoning


# Global model instance
_bail_model = None


def get_bail_model() -> BailEligibilityModel:
    """Get or create the global bail model instance."""
    global _bail_model
    if _bail_model is None:
        _bail_model = BailEligibilityModel()
    return _bail_model


def initialize_bail_model(dataset: List[Dict]) -> Dict:
    """Initialize and train the bail model."""
    model = get_bail_model()
    return model.train(dataset)
