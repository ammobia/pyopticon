"""
Dashboard State Manager for PyOpticon

This module provides functions to load and apply dashboard states from YAML files.
It allows defining named states that configure multiple widgets at once.

Currently, this module only supports valve configurations. Future versions may support
configuring other widget types.
"""

import os
import yaml
from typing import Dict, Any, Optional, Callable


class DashboardStateManager:
    """Manages dashboard states loaded from YAML configuration files."""
    
    def __init__(self, states_file: str):
        """
        Initialize the DashboardStateManager.
        
        Args:
            states_file: Path to the dashboard states YAML file
        """
        self.states_file = states_file
        self.states = self._load_states()
        
    def _load_states(self) -> Dict[str, Dict[str, Any]]:
        """Load dashboard states from YAML file."""
        if not os.path.exists(self.states_file):
            raise FileNotFoundError(f"Could not find {self.states_file}")
        
        with open(self.states_file, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('states', {})
    
    def get_state(self, state_name: str) -> Dict[str, Any]:
        """
        Get a specific dashboard state configuration.
        
        Args:
            state_name: Name of the state to retrieve
            
        Returns:
            Dictionary containing the state configuration
        """
        if state_name not in self.states:
            available_states = ', '.join(self.states.keys())
            raise ValueError(f"Unknown state '{state_name}'. Available states: {available_states}")
        
        return self.states[state_name]
    
    def list_states(self) -> list:
        """List all available dashboard states."""
        return list(self.states.keys())
    
    def apply_state(self, state_name: str, dashboard):
        """
        Apply a dashboard state.
        
        Currently only supports valve configurations. Future versions may support
        other widget types.
        
        Args:
            state_name: Name of the state to apply
            dashboard: PyOpticon dashboard object
        """
        state = self.get_state(state_name)
        
        print(f"Applying dashboard state: {state_name}")
        if 'description' in state:
            print(f"  Description: {state['description']}")
        
        # Currently only support valve configurations
        valve_config = state.get('valves', {})
        if not valve_config:
            print(f"  Warning: State '{state_name}' has no valve configuration")
            return
            
        self._apply_valve_config(valve_config, dashboard)
        
        # Warn about unsupported configurations
        unsupported_keys = [k for k in state.keys() if k not in ['description', 'valves']]
        if unsupported_keys:
            print(f"  Warning: State '{state_name}' contains unsupported configuration keys: {unsupported_keys}")
            print("  Currently only 'valves' configurations are supported.")
    
    def _apply_valve_config(self, valve_config: Dict[int, str], dashboard):
        """Apply valve configurations."""
        try:
            valves_widget = dashboard.get_widget_by_nickname("Valves")
        except KeyError:
            print("  Warning: No 'Valves' widget found on dashboard")
            return
            
        for valve_index, position in valve_config.items():
            if position == 'open':
                valves_widget.valve_open(valve_index)
            elif position == 'closed':
                valves_widget.valve_close(valve_index)
            else:
                print(f"  Warning: Unknown valve position '{position}' for valve {valve_index}")


# Helper functions for use in automation scripts

def create_state_manager(states_file: str) -> DashboardStateManager:
    """
    Create a DashboardStateManager instance.
    
    Args:
        states_file: Path to the dashboard states YAML file
        
    Returns:
        DashboardStateManager instance
    """
    return DashboardStateManager(states_file)


def schedule_dashboard_state(state_name: str, states_file: str):
    """
    Schedule a dashboard state change in an automation script.
    
    This function should be called within an automation script to schedule
    a dashboard state change. It uses schedule_function to queue the state change.
    
    Currently only valve configurations are supported in the state definitions.
    
    Args:
        state_name: Name of the state to apply
        states_file: Path to the dashboard states YAML file
    
    Example:
        # At the top of your automation script:
        STATES_FILE = "my_dashboard_states.yaml"
        
        # In your automation sequence:
        schedule_dashboard_state('flow_through', STATES_FILE)
        schedule_delay(delay="00:10:00")
        schedule_dashboard_state('bypass', STATES_FILE)
    """
    def apply_state_wrapper(dashboard):
        manager = DashboardStateManager(states_file)
        manager.apply_state(state_name, dashboard)
    
    # Note: schedule_function is available in the automation script namespace
    schedule_function(apply_state_wrapper)


def get_dashboard_states(states_file: str) -> list:
    """
    Get list of available states from a dashboard states file.
    
    Args:
        states_file: Path to the dashboard states YAML file
        
    Returns:
        List of available state names
    """
    manager = DashboardStateManager(states_file)
    return manager.list_states()


def create_state_scheduler(states_file: str) -> Callable:
    """
    Create a state scheduling function bound to a specific states file.
    
    This is useful when you want to avoid repeating the states_file parameter.
    
    Args:
        states_file: Path to the dashboard states YAML file
        
    Returns:
        Function that takes state_name and schedules the state change
        
    Example:
        # At the top of your automation script:
        schedule_state = create_state_scheduler("my_dashboard_states.yaml")
        
        # In your automation sequence:
        schedule_state('flow_through')
        schedule_delay(delay="00:10:00")
        schedule_state('bypass')
        
        # The YAML file should define states like:
        # states:
        #   flow_through:
        #     description: "Flow through reactor"
        #     valves:
        #       0: open
        #       1: closed
        #   bypass:
        #     description: "Bypass reactor"  
        #     valves:
        #       0: closed
        #       1: open
    """
    manager = DashboardStateManager(states_file)
    
    def schedule_state(state_name: str):
        def apply_state_wrapper(dashboard):
            manager.apply_state(state_name, dashboard)
        schedule_function(apply_state_wrapper)
    
    return schedule_state