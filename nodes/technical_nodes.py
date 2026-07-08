from graph.state import SupportState


def diagnose_application_error(state: SupportState) -> dict:
    return {
        "diagnostic_result": (
            "Check the application logs, restart the application, "
            "and verify that the latest version is installed."
        ),
        "resolution_status": "resolved",
    }


def diagnose_performance_issue(state: SupportState) -> dict:
    return {
        "diagnostic_result": (
            "Check the network connection, system resource usage, "
            "and whether the service is experiencing high load."
        ),
        "resolution_status": "resolved",
    }


def diagnose_feature_issue(state: SupportState) -> dict:
    return {
        "diagnostic_result": (
            "Verify the feature configuration, required permissions, "
            "and whether the feature is available for the customer."
        ),
        "resolution_status": "resolved",
    }


def diagnose_other_technical(state: SupportState) -> dict:
    return {
        "diagnostic_result": (
            "The technical issue could not be diagnosed automatically."
        ),
        "resolution_status": "unresolved",
    }

def prepare_technical_response(state: SupportState) -> dict:
    return {
        "response": (
            "Technical diagnosis completed. "
            f"{state['diagnostic_result']}"
        )
    }


def mark_for_escalation(state: SupportState) -> dict:
    return {
        "escalation_required": True,
        "escalation_reason": "automatic_diagnosis_failed",
    }
