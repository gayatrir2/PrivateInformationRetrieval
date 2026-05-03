# CMakeList.txt : CMake project for oldSEAL, include source and define
# project specific logic here.
#
cmake_minimum_required (VERSION 3.8)

# Enable Hot Reload for MSVC compilers if supported.
if (POLICY CMP0141)
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()

project ("oldSEAL")

# Add source to this project's executable.


include(FetchContent)

FetchContent_Declare(
  seal
  GIT_REPOSITORY https://github.com/microsoft/SEAL.git
  GIT_TAG v3.6.6
)

FetchContent_MakeAvailable(seal)

#SEAL PIR building

add_library(sealpir pir.hpp pir.cpp pir_client.hpp pir_client.cpp pir_server.hpp
  pir_server.cpp)

target_link_libraries(sealpir PUBLIC SEAL::seal)

#PIR library built?

add_executable (oldSEAL "oldSEAL.cpp" "oldSEAL.h")
target_link_libraries(oldSEAL sealpir)

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET oldSEAL PROPERTY CXX_STANDARD 20)
endif()

# TODO: Add tests and install targets if needed.
