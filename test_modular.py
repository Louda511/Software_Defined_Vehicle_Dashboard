"""
Simple test script to verify the modular structure works correctly
"""
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully"""
    try:
        from models.feature import Feature
        print("✓ models.feature imported successfully")
        
        from utils.file_utils import load_features, load_installed_images
        print("✓ utils.file_utils imported successfully")
        
        from services.podman_service import PodmanWorker
        print("✓ services.podman_service imported successfully")
        
        from ui.dialogs import FeatureDialog, DownloadInstallDialog
        print("✓ ui.dialogs imported successfully")
        
        from ui.components import FeatureCard, Dashboard
        print("✓ ui.components imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_feature_model():
    """Test the Feature model"""
    try:
        from models.feature import Feature
        
        # Test creating a feature from dict
        feature_data = {
            'name': 'Test Feature',
            'short_desc': 'Short description',
            'long_desc': 'Long description',
            'icon': 'test_icon.png',
            'location': 'https://hub.docker.com/_/test'
        }
        
        feature = Feature.from_dict(feature_data)
        assert feature.name == 'Test Feature'
        assert feature.short_desc == 'Short description'
        print("✓ Feature model works correctly")
        return True
    except Exception as e:
        print(f"✗ Feature model test failed: {e}")
        return False

def test_file_utils():
    """Test file utility functions"""
    try:
        from utils.file_utils import extract_image_name
        
        # Test image name extraction
        result1 = extract_image_name('https://hub.docker.com/_/hello-world')
        result2 = extract_image_name('https://hub.docker.com/r/user/image')
        
        assert result1 == 'hello-world', f"Expected 'hello-world', got '{result1}'"
        assert result2 == 'image', f"Expected 'image', got '{result2}'"
        
        print("✓ File utils work correctly")
        return True
    except Exception as e:
        print(f"✗ File utils test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Testing modular structure...")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_feature_model,
        test_file_utils
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Modular structure is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == '__main__':
    main() 