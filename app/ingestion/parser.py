import re
from typing import Optional


class AuthLogParser:
    LOG_PATTERN = re.compile(
        r'(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(?P<hostname>\S+)\s+'
        r'(?P<service>\w+)\[(?P<pid>\d+)\]:\s+'
        r'(?P<message>.*)'
    )
    IP_PATTERN = re.compile(r'from\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    USER_PATTERN = re.compile(r'for\s+(?:invalid user\s+)?(\w+)')

    def parse_line(self, line: str) -> Optional[dict]:
        if not line or not line.strip():
            return None
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            return None
        data = match.groupdict()
        message = data['message']
        ip_match = self.IP_PATTERN.search(message)
        data['ip'] = ip_match.group(1) if ip_match else "Unknown"
        user_match = self.USER_PATTERN.search(message)
        data['user'] = user_match.group(1) if user_match else "Unknown"
        data['event_type'] = self._classify_event(message)
        return data

    @staticmethod
    def _classify_event(message: str) -> str:
        m = message.lower()
        if "failed password" in m: return "Failed Login"
        if "accepted password" in m: return "Successful Login"
        if "invalid user" in m: return "Invalid User Attempt"
        if "connection closed" in m: return "Connection Closed"
        if "disconnected" in m: return "Disconnected"
        return "Other"
