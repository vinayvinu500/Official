import nh3

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
