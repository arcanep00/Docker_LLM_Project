MAX_RETRIES = 3

BACKOFF_SECONDS = [
    2,
    4,
    8
]

import time

import json

import google.generativeai as genai

from app.config import GEMINI_API_KEY


# Configure Gemini
genai.configure(
    api_key=GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)
def safe_gemini_call(prompt):

    last_error = None

    for attempt in range(
        MAX_RETRIES
    ):
        print(f"Attempt {attempt + 1}")

        try:

            response = (
                model.generate_content(
                    prompt
                )
            )

            return response.text

        except Exception as e:

            last_error = str(e)

            print(
                f"Gemini Error: {e}"
            )

            if (
                attempt <
                MAX_RETRIES - 1
            ):

                time.sleep(
                    BACKOFF_SECONDS[
                        attempt
                    ]
                )

    raise Exception(
        last_error
    )

def get_uncategorised_rows(df):
    return df[
        df["category"] == "Uncategorised"
    ]


def build_prompt(merchants):
    prompt = f"""
Classify the following merchants.

Allowed categories:

Food
Shopping
Travel
Transport
Utilities
Cash Withdrawal
Entertainment
Other

Return ONLY valid JSON.

Do not return markdown.

Do not return code blocks.

Do not return explanations.

Do not return any text before or after the JSON.

Every merchant must have exactly one category.

Output format:

{{
    "merchant_name": "category"
}}

Example:

{{
    "Swiggy": "Food",
    "Uber": "Transport",
    "Amazon": "Shopping",
    "Netflix": "Entertainment"
}}

Merchants:

{merchants}
"""

    return prompt


def classify_merchants(merchants):
    """
    Returns:
    (
        classifications,
        raw_response,
        llm_failed
    )
    """

    prompt = build_prompt(
        merchants
    )

    try:

        response_text = (
            safe_gemini_call(
                prompt
            )
        )

        raw_response = response_text

        if not raw_response:
            return (
                {},
                "Empty response from Gemini",
                True
            )

        response_text = (
            raw_response
            .replace(
                "```json",
                ""
            )
            .replace(
                "```JSON",
                ""
            )
            .replace(
                "```",
                ""
            )
            .strip()
        )

        try:

            classifications = json.loads(
                response_text
            )

            return (
                classifications,
                raw_response,
                False
            )

        except json.JSONDecodeError as e:

            print(
                f"JSON parsing failed: {e}"
            )

            print(
                f"Raw Gemini response: {raw_response}"
            )

            return (
                {},
                raw_response,
                True
            )

    except Exception as e:

        print(
            f"Gemini API failed: {e}"
        )

        return (
            {},
            "",
            True
        )

def apply_categories(
    df,
    classifications
):
    for idx, row in df.iterrows():

        merchant = row["merchant"]

        if merchant in classifications:

            category = classifications[
                merchant
            ]

            df.loc[
                idx,
                "llm_category"
            ] = category

            df.loc[
                idx,
                "category"
            ] = category

    return df


def enrich_categories(df):

    uncategorised = (
        get_uncategorised_rows(df)
    )

    if len(
            uncategorised
    ) == 0:
        return df

    merchants = (
        uncategorised[
            "merchant"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    if not merchants:
        return df

    (
        classifications,
        raw_response,
        llm_failed
    ) = classify_merchants(
        merchants
    )

    df = apply_categories(
        df,
        classifications
    )

    # Store Gemini metadata
    df["llm_raw_response"] = (
        raw_response
    )

    df["llm_failed"] = (
        llm_failed
    )

    return df