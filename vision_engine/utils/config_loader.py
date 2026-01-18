"""
Configuration loader for vision engine.

Supports loading from YAML files with validation.
"""

import os
from typing import Optional
import yaml
from ..types import VisionConfig


def load_config(config_path: Optional[str] = None) -> VisionConfig:
    """
    Load vision engine configuration from file.

    Args:
        config_path: Path to YAML config file.
                     If None, uses default config.

    Returns:
        VisionConfig instance

    Raises:
        FileNotFoundError: If config file not found
        ValueError: If configuration is invalid
    """
    if config_path is None:
        # Use default config
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'config',
            'default_config.yaml'
        )

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Load YAML
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)

    # Create VisionConfig
    config = VisionConfig(**config_dict)

    # Validate
    errors = config.validate()
    if errors:
        raise ValueError(f"Invalid configuration: {', '.join(errors)}")

    return config


def save_config(config: VisionConfig, output_path: str) -> None:
    """
    Save configuration to YAML file.

    Args:
        config: VisionConfig instance
        output_path: Path to save YAML file
    """
    # Convert to dict
    config_dict = {
        'anomaly_threshold': config.anomaly_threshold,
        'enable_crack_detector': config.enable_crack_detector,
        'enable_hole_detector': config.enable_hole_detector,
        'enable_anomaly_detector': config.enable_anomaly_detector,
        'crack_min_length': config.crack_min_length,
        'crack_max_width': config.crack_max_width,
        'crack_confidence_threshold': config.crack_confidence_threshold,
        'hole_min_area': config.hole_min_area,
        'hole_max_area': config.hole_max_area,
        'hole_circularity_threshold': config.hole_circularity_threshold,
        'resize_width': config.resize_width,
        'resize_height': config.resize_height,
        'use_gpu': config.use_gpu,
    }

    # Save to YAML
    with open(output_path, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False)

    print(f"Configuration saved to {output_path}")
