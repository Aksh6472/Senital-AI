"""
AI Pipeline — Stage 5: AI Decision Engine & Explainability Generator.
"""

from __future__ import annotations

from typing import Any

from backend.ai_pipeline.base_contracts import AggregatedFrameSignal, DecisionResult, FrameContext

INCIDENT_RULESET = {
    "weapon_detected": {
        "incident_type": "weapon_threat",
        "default_severity": "critical",
        "default_priority": "P1",
        "default_threshold": 0.75,
        "requires_multi_signal": True,
        "response": "Dispatch immediate armed response. Alert site security control.",
    },
    "fight_assault": {
        "incident_type": "fight_assault",
        "default_severity": "high",
        "default_priority": "P1",
        "default_threshold": 0.70,
        "requires_multi_signal": True,
        "response": "Dispatch security patrol to zone immediately. Review live feed.",
    },
    "fall_collapse": {
        "incident_type": "medical_emergency",
        "default_severity": "high",
        "default_priority": "P2",
        "default_threshold": 0.65,
        "requires_multi_signal": False,
        "response": "Alert medical/first-aid responder. Verify camera audio.",
    },
    "fire_smoke": {
        "incident_type": "fire_hazard",
        "default_severity": "critical",
        "default_priority": "P1",
        "default_threshold": 0.70,
        "requires_multi_signal": False,
        "response": "Trigger fire suppression warning. Contact emergency fire department.",
    },
    "perimeter_breach": {
        "incident_type": "intrusion",
        "default_severity": "medium",
        "default_priority": "P2",
        "default_threshold": 0.60,
        "requires_multi_signal": False,
        "response": "Verify perimeter barrier and issue automated audio warning.",
    },
    "loitering": {
        "incident_type": "suspicious_activity",
        "default_severity": "low",
        "default_priority": "P3",
        "default_threshold": 0.65,
        "requires_multi_signal": False,
        "response": "Log event for security patrol routine check.",
    },
}


class DecisionEngine:
    def __init__(self, global_confidence_threshold: float = 0.60):
        self.global_confidence_threshold = global_confidence_threshold

    def evaluate(
        self,
        signal: AggregatedFrameSignal,
        context: FrameContext,
    ) -> DecisionResult:
        if not signal.detected_objects and not signal.detected_actions:
            return DecisionResult(should_alert=False)

        active_config = context.active_modules_config.get("config", {})
        threshold_override = active_config.get("confidence_threshold", self.global_confidence_threshold)

        detected_obj_classes = {o["class_name"]: o["aggregated_confidence"] for o in signal.detected_objects}
        detected_act_codes = {a["action_code"]: a["aggregated_confidence"] for a in signal.detected_actions}

        matched_incident_type = None
        highest_rule_severity = "low"
        highest_rule_priority = "P4"
        matched_response = ""
        multi_signal_corroborated = False

        if "weapon" in detected_obj_classes:
            weapon_conf = detected_obj_classes["weapon"]
            rule = INCIDENT_RULESET["weapon_detected"]
            has_action = "weapon_brandishing" in detected_act_codes or "running_panic" in detected_act_codes
            is_corroborated = has_action or signal.sample_count >= 10

            if weapon_conf >= threshold_override:
                matched_incident_type = rule["incident_type"]
                highest_rule_severity = rule["default_severity"]
                highest_rule_priority = rule["default_priority"]
                matched_response = rule["response"]
                multi_signal_corroborated = is_corroborated

        elif "fire_smoke" in detected_obj_classes:
            fire_conf = detected_obj_classes["fire_smoke"]
            rule = INCIDENT_RULESET["fire_smoke"]
            if fire_conf >= threshold_override:
                matched_incident_type = rule["incident_type"]
                highest_rule_severity = rule["default_severity"]
                highest_rule_priority = rule["default_priority"]
                matched_response = rule["response"]
                multi_signal_corroborated = True

        elif "fighting_gesture" in detected_act_codes:
            fight_conf = detected_act_codes["fighting_gesture"]
            rule = INCIDENT_RULESET["fight_assault"]
            is_corroborated = signal.tracked_subjects_count >= 2
            if fight_conf >= threshold_override:
                matched_incident_type = rule["incident_type"]
                highest_rule_severity = rule["default_severity"]
                highest_rule_priority = rule["default_priority"]
                matched_response = rule["response"]
                multi_signal_corroborated = is_corroborated

        elif "fall_collapse" in detected_act_codes:
            fall_conf = detected_act_codes["fall_collapse"]
            rule = INCIDENT_RULESET["fall_collapse"]
            if fall_conf >= threshold_override:
                matched_incident_type = rule["incident_type"]
                highest_rule_severity = rule["default_severity"]
                highest_rule_priority = rule["default_priority"]
                matched_response = rule["response"]
                multi_signal_corroborated = True

        elif "loitering" in detected_act_codes:
            loiter_conf = detected_act_codes["loitering"]
            rule = INCIDENT_RULESET["loitering"]
            if loiter_conf >= threshold_override:
                matched_incident_type = rule["incident_type"]
                highest_rule_severity = rule["default_severity"]
                highest_rule_priority = rule["default_priority"]
                matched_response = rule["response"]
                multi_signal_corroborated = True

        if not matched_incident_type or signal.aggregated_confidence < threshold_override:
            return DecisionResult(should_alert=False)

        obj_summary = ", ".join([f"{o['class_name']} ({int(o['aggregated_confidence']*100)}%)" for o in signal.detected_objects]) or "None"
        act_summary = ", ".join([f"{a['action_code']} ({int(a['aggregated_confidence']*100)}%)" for a in signal.detected_actions]) or "None"

        explanation = (
            f"Incident '{matched_incident_type}' flagged on Camera {context.camera_id}. "
            f"Detected objects: [{obj_summary}], detected actions: [{act_summary}]. "
            f"Aggregated signal confidence: {int(signal.aggregated_confidence * 100)}% across {signal.sample_count} sampled frames. "
            f"Corroboration rule passed: {multi_signal_corroborated}. Assigned severity: {highest_rule_severity.upper()} ({highest_rule_priority})."
        )

        return DecisionResult(
            should_alert=True,
            incident_type_code=matched_incident_type,
            severity=highest_rule_severity,
            priority=highest_rule_priority,
            confidence_score=signal.aggregated_confidence,
            ai_explanation=explanation,
            recommended_response=matched_response,
            detected_objects=signal.detected_objects,
            detected_actions=signal.detected_actions,
            multi_signal_corroborated=multi_signal_corroborated,
        )
