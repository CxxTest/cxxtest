FIND_PROGRAM(CXXTESTGEN
    NAMES cxxtestgen
    PATHS ./cxxtest/bin/
          /usr/bin
          /bin
          )

IF(NOT CXXTESTGEN)
    MESSAGE(FATAL_ERROR "Unable to find 'cxxtestgen'")
ENDIF(NOT CXXTESTGEN)
