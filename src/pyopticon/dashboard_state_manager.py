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
            valves_widget = dashboard.get_widget_by_nickname("Valve Widget")
        except KeyError:
            print("  Warning: No 'Valve Widget' widget found on dashboard")
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