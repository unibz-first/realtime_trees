import os
from pathlib import Path
import subprocess

from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, EnvironmentVariable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterFile


def _can_run_node(python_executable: Path) -> bool:
    if not python_executable.is_file():
        return False
    try:
        subprocess.run(
            [str(python_executable), '-c', 'import rclpy, trimesh, open3d'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=5.0,
        )
    except (subprocess.SubprocessError, OSError):
        return False
    return True


def _node_prefix() -> str:
    candidates = []

    override_python = os.environ.get('REALTIME_TREES_PYTHON_EXECUTABLE')
    if override_python:
        candidates.append(Path(override_python))

    package_prefix = Path(get_package_prefix('realtime_trees_ros')).resolve()
    search_roots = [package_prefix, Path(__file__).resolve()]
    for search_root in search_roots:
        for parent in search_root.parents:
            candidates.append(parent / 'src' / 'realtime_trees' / 'realtime_trees_ros' / 'env' / 'bin' / 'python3')

    virtual_env = os.environ.get('VIRTUAL_ENV')
    if virtual_env:
        candidates.append(Path(virtual_env) / 'bin' / 'python3')

    for python_executable in candidates:
        if _can_run_node(python_executable):
            return f'{python_executable} '

    return ''


def generate_launch_description() -> LaunchDescription:
    parameters_file = LaunchConfiguration('params')
    use_sim_time = LaunchConfiguration('use_sim_time')

    default_use_sim_time = EnvironmentVariable('USE_SIM_TIME', default_value='false')
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value=default_use_sim_time,
        description='Use simulation time'
    )
    default_parameters_file = os.path.join(
        get_package_share_directory('realtime_trees_ros'),
        'config',
        'realtime_trees_config_treescope.yaml'
    )
    realtime_trees_parameters_arg = DeclareLaunchArgument(
        'params',
        default_value=default_parameters_file,
        description='Parameters file to be used'
    )

    realtime_trees_node = Node(
        package='realtime_trees_ros',
        executable='realtime_trees_node',
        parameters=[ParameterFile(parameters_file, allow_substs=True),
                    {'use_sim_time': use_sim_time}],
        output='screen',
        emulate_tty=True, # For outputting regular print statements to the terminal!
        prefix=_node_prefix()
    )

    ld = LaunchDescription()
    ld.add_action(use_sim_time_arg)
    ld.add_action(realtime_trees_parameters_arg)
    ld.add_action(realtime_trees_node)
    return ld
