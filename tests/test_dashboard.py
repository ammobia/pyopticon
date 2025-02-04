import pytest
from pyopticon.dashboard import PyOpticonDashboard

def mock_interlock():
    print("Mock interlock function called")
    pass

def test_set_interlocks_disabled():
    dashboard = PyOpticonDashboard("Test Dashboard")
    
    # Add a mock interlock function
    dashboard.add_interlock(mock_interlock)
    
    # Disable interlocks
    dashboard.set_interlocks_disabled(True)
    assert dashboard.interlocks_disabled == True
    assert dashboard.all_interlocks == []
    assert dashboard.disabled_interlocks == [mock_interlock]
    
    # Enable interlocks
    dashboard.set_interlocks_disabled(False)
    assert dashboard.interlocks_disabled == False
    assert dashboard.all_interlocks == [mock_interlock]
    assert dashboard.disabled_interlocks == []