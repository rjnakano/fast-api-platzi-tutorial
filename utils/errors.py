from pydantic import UrlError

# Errors
class FacebookUrlDomainError(UrlError):
    code = 'facebook.domain'
    msg_template = f"invalid facebook domain, should be: 'https://www.facebook.com'"

class FacebookUrlProfileError(UrlError):
    code = 'facebook.profile'
    msg_template = f"invalid facebook profile"    