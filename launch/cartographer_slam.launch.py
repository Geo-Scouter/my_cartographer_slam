#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch.actions import RegisterEventHandler, EmitEvent
from launch_ros.actions import LifecycleNode, Node
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.events import matches_action
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    use_sim_time = DeclareLaunchArgument('use_sim_time', default_value='false')

    # Cartographer の設定ファイルパス
    cartographer_config_dir = os.path.join(
        get_package_share_directory('my_cartographer_slam'),
        'config'
    )
    configuration_basename = 'cartographer_2d.lua'

    # urg_node2 の LifecycleNode 定義
    urg_node = LifecycleNode(
        package='urg_node2',
        executable='urg_node2_node',
        name='urg_node2',
        output='screen',
        namespace='',#lifecycleNodeだから必要
        parameters=[{
            'ip_address': '192.168.4.61',
            'ip_port': 10940,
            'frame_id': 'laser_link',
            'publish_intensity': False,
            'publish_multiecho': False
        }]
    )

    # `unconfigured` → `configured` に遷移 (確実に実行するため TimerAction を追加)
    configure_urg = TimerAction(
        period=3.0,  # 起動後 3 秒後に実行
        actions=[
            EmitEvent(
                event=ChangeState(
                    lifecycle_node_matcher=matches_action(urg_node),
                    transition_id=1,  # `unconfigured` → `configured`
                )
            )
        ]
    )

    # `configured` → `active` に遷移 (確実に実行するため TimerAction を追加)
    activate_urg = TimerAction(
        period=6.0,
        actions=[
            EmitEvent(
                event=ChangeState(
                    lifecycle_node_matcher=matches_action(urg_node),
                    transition_id=3,  # `configured` → `active`
                )
            )
        ]
    )

    # TF 固定変換 (base_link → laser_link)
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_pub',
        output='screen',
        arguments=[
            '0.2', '0.0', '0.1',     # x, y, z
            '0.0', '0.0', '0.0', '1.0',  # qx, qy, qz, qw
            'base_link',
            'laser_link'
        ]
    )

    # Cartographer ノード
    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': False}],
        arguments=[
            '-configuration_directory', cartographer_config_dir,
            '-configuration_basename', configuration_basename
        ],
        remappings=[
            ('scan', '/scan')
        ]
    )

    # Occupancy Grid ノード (地図を生成するノード)
    occupancy_grid_node = Node(
         package='cartographer_ros',
         executable='cartographer_occupancy_grid_node',
         name='cartographer_occupancy_grid_node',
         output='screen',
         parameters=[{'use_sim_time': False}],
         arguments=[
             '-resolution', '0.05',
             '-publish_period_sec', '1.0'
         ],
     )

    # RViz ノード
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=[
            '-d', os.path.join(
                get_package_share_directory('cartographer_ros'),
                'config', 'rviz2_default.rviz'
            )
        ]
    )

    return LaunchDescription([
        use_sim_time,
        urg_node,
        configure_urg,
        activate_urg,
        static_tf,
        cartographer_node,
        occupancy_grid_node,
        rviz_node
    ])
