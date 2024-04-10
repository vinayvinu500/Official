import nh3
import re
import json

# https://daniel.feldroy.com/posts/2023-06-converting-from-bleach-to-nh3
# https://nh3.readthedocs.io/en/latest/
def sanitize_html(html_content: str) -> str:
    # Define allowed HTML tags
    allowed_tags = {
        'p', 'b', 'i', 'u', 'em', 'strong', 'a', 'ul', 'ol', 'li',
        'font', 'span', 'img', 'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot'
    }

    # Define allowed attributes for each tag
    allowed_attributes = {
        'a': {'href', 'title'},
        'img': {'src', 'alt'},
        'span': {'style'},  # Assuming you will handle CSS sanitization as needed
        'p': {'style'},
        # Add any additional tags and attributes as per your requirements
    }

    # Define allowed URL schemes
    allowed_url_schemes = {'http', 'https', 'mailto'}

    # Sanitize the HTML content
    safe_html = nh3.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        url_schemes=allowed_url_schemes,
    )

    return safe_html

# Utility function for sanitizing inputs
def sanitize_input(input_value: str) -> str:
    # This pattern matches against common SQL injection tactics and JavaScript code injection
    pattern = r"(--|\b(ALTER|CREATE|DELETE|DROP|EXECUTE|INSERT INTO|MERGE|SELECT|UPDATE|UNION ALL|UNION SELECT)\b|<script>|<\/script>)"
    
    # Remove matched patterns
    sanitized_value = re.sub(pattern, "", input_value, flags=re.IGNORECASE)
    
    # Additional steps could be to escape other special characters or remove them
    sanitized_value = re.sub(r"[<>{}]", "", sanitized_value)
    
    # Trim leading and trailing whitespace
    sanitized_value = sanitized_value.strip()

    return sanitized_value


def validate_json_structure(question):
    """
    Validate the structure of the question JSON.
    Expected to have 'description', 'database_schema', and 'sample_solution'.
    """
    required_keys = {'description', 'database_schema', 'sample_solution'}
    return required_keys.issubset(question.keys())

def content_review(question, topic, difficulty_level, language):
    """
    Review the content of the question for adherence to topic, difficulty level, and language specificity.
    This is a simplified check and might need more sophisticated NLP tools for deeper analysis.
    """
    # Simple checks for topic and difficulty level in the description
    # This could be expanded with more sophisticated NLP analysis for better accuracy
    if topic.lower() in question['description'].lower() and difficulty_level.lower() in question['description'].lower():
        return True
    return False