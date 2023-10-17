
include("${CMAKE_CURRENT_LIST_DIR}/FindCxxTest.cmake")

function(cxx_test target source)
    get_filename_component(CPP_FILE_NAME ${source} NAME)
    string(REGEX REPLACE "h$|hpp$" "cpp" CPP_FILE_NAME ${CPP_FILE_NAME})
    message(${CPP_FILE_NAME})
    set(CPP_FULL_NAME "${CMAKE_CURRENT_BINARY_DIR}/${CPP_FILE_NAME}")
    add_custom_command(
        OUTPUT "${CPP_FULL_NAME}"
        COMMAND ${CXXTESTGEN} --runner=ErrorPrinter --output "${CPP_FULL_NAME}" "${source}"
        DEPENDS "${source}"
    )
    add_executable(${target} ${CPP_FULL_NAME})
    set_target_properties(${target} PROPERTIES COMPILE_FLAGS "-Wno-effc++")
    add_test(${target} ${RUNTIME_OUTPUT_DIRECTORY}/${target})
endfunction(cxx_test)

if(NOT DEFINED CXXTEST_TESTGEN_ARGS)
  set(CXXTEST_TESTGEN_ARGS --error-printer)
endif()
macro(CXXTEST_ADD_TEST _cxxtest_testname _cxxtest_outfname)
  set(_cxxtest_real_outfname ${CMAKE_CURRENT_BINARY_DIR}/${_cxxtest_outfname})

  include_directories(${CXXTEST_INCLUDE_DIRS})
  add_custom_command(
    OUTPUT  ${_cxxtest_real_outfname}
    DEPENDS ${ARGN}
    COMMAND ${CXXTESTGEN} ${CXXTEST_TESTGEN_ARGS} --world=${_cxxtest_outfname} -o ${_cxxtest_real_outfname} ${ARGN} 
    )
  set_source_file_properties(${_cxxtest_real_outfname} PROPERTIES GENERATED true)
  add_executable(${_cxxtest_testname) ${_cxxtest_real_outfname} ${ARGN})
  if(CMAKE_RUNTIME_OUTPUT_DIRECTORY)
    add_test(${_cxxtest_testname} ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${_cxxtest_testname})
  elseif(EXECUTABLE_OUTPUT_PATH)
    add_test(${_cxxtest_testname} ${EXECUTABLE_OUTPUT_PATH}/${_cxxtest_testname})
  else()
    add_test(${_cxxtest_testname} ${CMAKE_CURRENT_BINARY_DIR}/${_cxxtest_testname})
  endif()

macro(CXXTEST_ADD_TEST)

