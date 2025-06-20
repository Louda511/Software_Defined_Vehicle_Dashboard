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
        description = data.get('description', '')
        
        # Split description into short and long versions
        parts = description.split('.', 1)
        short_desc = parts[0] + '.' if len(parts) > 0 else description
        long_desc = description
        
        return cls(
            name=data.get('name', ''),
            short_desc=short_desc.strip(),
            long_desc=long_desc.strip(),
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