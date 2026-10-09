import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value=EnvironmentVariable('USE_SIM_TIME', default_value='false'),
        description='Use simulation time',
    )

    package_dir = get_package_share_directory('realtime_trees_ros')
    rviz_config_file = os.path.join(package_dir, 'rviz', 'realtime_trees.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='realtime_trees_rviz',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    ld = LaunchDescription()
    ld.add_action(use_sim_time_arg)
    ld.add_action(rviz_node)
    return ld
