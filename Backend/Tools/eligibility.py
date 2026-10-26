
from Backend.Tools.policy_search import search_policy


def check_policy_eligibility(question: str) -> str:
    """Retrieve policy evidence without making unsupported decisions."""

    if not question.strip():
        return "Please provide details about your policy-related case."

    policy_context = search_policy(question)

    if (
        not policy_context.strip()
        or "No relevant policy information was found." in policy_context
        or "Please provide a policy question." in policy_context
    ):
        return (
            "Eligibility cannot be assessed because sufficient policy "
            "evidence was not found. Please consult the applicable "
            "official Airbnb policy."
        )

    return (
        "Eligibility status: UNDETERMINED.\n\n"
        "The following policy evidence was retrieved, but eligibility "
        "has not been confirmed. The applicable policy conditions must "
        "be compared with the user's specific circumstances. If booking "
        "details or required conditions are missing, ask the user for "
        "that information. Do not assume eligibility from this evidence.\n\n"
        f"{policy_context}"
    )
