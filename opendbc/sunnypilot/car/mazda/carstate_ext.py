"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from enum import StrEnum

from opendbc.car import Bus, structs
from opendbc.can.parser import CANParser
from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.mazda.values import CAR
from openpilot.common.params import Params


class CarStateExt:
  def __init__(self, CP, CP_SP):
    self.CP = CP
    self.CP_SP = CP_SP
    self.params = Params()

  def update(self, ret: structs.CarState, ret_sp: structs.CarStateSP, can_parsers: dict[StrEnum, CANParser]) -> None:
    cp_cam = can_parsers[Bus.cam]

    # CAM_TRAFFIC_SIGNS comes from the front camera. SPEED_SIGN_ON is the normal validity
    # flag. On the metric 2021-23 CX-9 it stays clear while SPEED_SIGN_CAM marks a camera
    # detection, so accept either flag on that platform without changing other Mazdas.
    sign = cp_cam.vl["CAM_TRAFFIC_SIGNS"]
    speed_sign = sign["SPEED_SIGN"]
    is_metric = self.params.get_bool("IsMetric")
    cx9_metric_camera_sign = is_metric and self.CP.carFingerprint == CAR.MAZDA_CX9_2021 and sign["SPEED_SIGN_CAM"] == 1
    valid_sign = sign["SPEED_SIGN_ON"] == 1 or cx9_metric_camera_sign
    if valid_sign and 0 < speed_sign <= 120:
      ret_sp.speedLimit = float(speed_sign) * (CV.KPH_TO_MS if is_metric else CV.MPH_TO_MS)
    else:
      ret_sp.speedLimit = 0.0
