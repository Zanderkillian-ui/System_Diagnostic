from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():

    dashboard = ExecuteProcess(
        cmd=["python3", "-m", "minion_diagnostic.widgets.main_dashboard"],
        output="screen"
    )

    return LaunchDescription([dashboard])