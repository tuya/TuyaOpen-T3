list_subdirectories(PLATFORM_PUBINC_1 ${PLATFORM_PATH}/tuyaos/tuyaos_adapter)

# Type headers: the platform copy of tuya_cloud_types.h lacks the TAL type
# aliases (INT_T / VOID_T / DLONG_T, ...); put this copy first so it wins.
list(INSERT PLATFORM_PUBINC_1 0 "${CMAKE_CURRENT_LIST_DIR}/tuyaos/tuyaos_adapter/tuyaopen/include/common")

# lwIP headers used by core_network.c
set(PLATFORM_PUBINC_2
    ${PLATFORM_PATH}/t3_os/tuya_build/bk7236/config
    ${PLATFORM_PATH}/t3_os/armino/include
    ${PLATFORM_PATH}/t3_os/armino/middleware/driver/include/bk_private
    ${PLATFORM_PATH}/t3_os/armino/components/lwip_intf_v2_1/lwip-2.1.2/port
    ${PLATFORM_PATH}/t3_os/armino/components/lwip_intf_v2_1/lwip-2.1.2/src/include
)

set(PLATFORM_PUBINC
    ${PLATFORM_PUBINC_1}
    ${PLATFORM_PUBINC_2})