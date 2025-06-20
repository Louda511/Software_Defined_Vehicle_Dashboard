"""
Feature model for representing application features
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Feature:
    """Represents a feature/app in the ADAS App Store"""
    name: str
    short_desc: str
    long_desc: str
    icon: str
    location: Optional[str] = None
    
    @property
    def image_name(self) -> str:
        """Extract image name from location URL"""
        if not self.location:
            return ""
        
        # For Docker Hub, extract the image name from the URL
        # e.g., https://hub.docker.com/_/hello-world -> hello-world
        if '/_/' in self.location:
            return self.location.split('/_/')[-1]
        elif '/r/' in self.location:
            return self.location.split('/r/')[-1]
        return self.location.split('/')[-1]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Feature':
        """Create a Feature instance from a dictionary"""
        return cls(
            name=data.get('name', ''),
            short_desc=data.get('short_desc', ''),
            long_desc=data.get('long_desc', ''),
            icon=data.get('icon', ''),
            location=data.get('location', '')
        )
    
    def to_dict(self) -> dict:
        """Convert Feature instance to dictionary"""
        return {
            'name': self.name,
            'short_desc': self.short_desc,
            'long_desc': self.long_desc,
            'icon': self.icon,
            'location': self.location
        } 