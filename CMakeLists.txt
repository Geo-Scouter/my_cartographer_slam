cmake_minimum_required(VERSION 3.8)
project(my_cartographer_slam)

# ROS 2 用のビルドツール
find_package(ament_cmake_auto REQUIRED)

# 明示的に必要なパッケージも追加（package.xml に記述済みなら不要な場合もあり）
find_package(rclcpp REQUIRED)
find_package(cartographer_ros REQUIRED)
#find_package(urg_node2 REQUIRED)
find_package(tf2_ros REQUIRED)

# package.xml に記述された依存関係を自動検出
ament_auto_find_build_dependencies()

#(自動)コンパイラがGNU C++コンパイラかClang系コンパイラのときにオプションを設定
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

install(
  DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # 以下はライセンス等のチェックをスキップする設定
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_auto_package()
