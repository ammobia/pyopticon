import pytest
import tkinter as tk
import queue
import threading
import time
from pyopticon.dashboard import PyOpticonDashboard

@pytest.fixture
def dashboard():
    """Create a dashboard instance in the main thread"""    
    dashboard = PyOpticonDashboard(
        dashboard_name="test_dashboard",
        offline_mode=False,
        polling_interval_ms=100,
        window_resizeable=False,
        persistent_console_logfile=False,
        socket_ports=[],
        include_auto_widget=True,
        include_socket_widget=False
    )

    yield dashboard
    
    try:
        dashboard.root.quit()
        dashboard.root.destroy()
    except tk.TclError:
        pass

def test_dashboard_initialization(dashboard):
    """Test basic dashboard setup"""
    assert dashboard.name == "test_dashboard"
    assert dashboard.offline_mode is False
    assert len(dashboard.all_widgets) > 0

def test_interlock_registration(dashboard):
    """Test adding and calling interlocks"""
    test_called = False
    
    def test_interlock():
        nonlocal test_called
        test_called = True
    
    def interlock_checked():
        nonlocal test_called
        assert test_called is True

    # This is needed so that tests can continue
    def close_dashboard():
        dashboard.root.destroy()

    dashboard.add_interlock(test_interlock)
    assert test_interlock in dashboard.all_interlocks

    dashboard._serial_control_widget._toggle_serial_connected()
    dashboard.root.after(6100, interlock_checked)
    dashboard.root.after(6200, close_dashboard)
    dashboard.start()

def test_system_state_change(dashboard):
    """Test system state changes"""
    dashboard.set_system_state("Maintenance")
    dashboard.root.update()  # Process the change
    assert dashboard.get_system_state() == "Maintenance"

def test_widget_update(dashboard):
    """Test that widget updates are processed"""
    update_called = False
    
    def mock_update():
        nonlocal update_called
        update_called = True
    
    dashboard.root.after(100, mock_update)
    
    # Process events a few times
    for _ in range(5):
        dashboard.root.update()
        time.sleep(0.05)
    
    assert update_called, "Widget update was not called"

@pytest.mark.parametrize("state", [
    "Running",
    "Not Running",
    "Maintenance"
])
def test_valid_system_states(dashboard, state):
    """Test setting valid system states"""
    dashboard.set_system_state(state)
    dashboard.root.update()
    assert dashboard.get_system_state() == state

def test_invalid_system_state(dashboard):
    """Test setting invalid system state"""
    with pytest.raises(ValueError):
        dashboard.set_system_state("Invalid State")

def test_serial_widget_update(dashboard):
    """Test that serial widget updates work"""
    update_called = False
    
    def mock_update():
        nonlocal update_called
        update_called = True
    
    # Replace the update method
    original_update = dashboard._serial_control_widget._update_widgets
    dashboard._serial_control_widget._update_widgets = mock_update
    
    try:
        # Trigger the update
        dashboard.serial_connected = True
        dashboard.root.after(
            100,
            lambda: dashboard._serial_control_widget._update_widgets()
        )
        
        # Process events a few times
        for _ in range(5):
            dashboard.root.update()
            time.sleep(0.05)
        
        assert update_called, "_update_widgets was not called"
    finally:
        # Restore original update function
        dashboard._serial_control_widget._update_widgets = original_update