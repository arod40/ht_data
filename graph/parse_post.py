import re
from phonenumbers import parse as phone_parse, is_valid_number


class Extractor:
    def extract(self, string):
        return [string[x.span()[0]:x.span()[1]] for x in re.finditer(self.regex, string)]


class RegexPhoneNumberExtractor(Extractor):
    regex = r"\+?[0-9-]+"

    def extract(self, string):
        ret = []
        for p in re.findall(self.regex, string):
            try:
                phone = phone_parse(p, "US")
                if is_valid_number(phone):
                    ret.append(str(phone.national_number))
            except:
                continue

        return ret


# Compliant with RFC 5322
# See https://stackoverflow.com/questions/201323/how-can-i-validate-an-email-address-using-a-regular-expression
class EmailExtractor(Extractor):
    regex = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"


class InstagramUsernameExtractor(Extractor):
    regex = r"\B@\w+(?:\.\w+)*"

class SnapchatUsernameExtractor(Extractor):
    regex =  r"\B@\w+(?:\.\w+)*"


class UrlExtractor(Extractor):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"


class TimeExtractor(Extractor):
    def extract(self, string: str):
        return [string.split("on")[0].strip()]

class DateExtractor(Extractor):
    def extract(self, string: str):
        return [string.split("on")[1].strip()]

class RegionExtractor(Extractor):
    def extract(self, string: str):
        return [string.split("\n")[0].strip()]