# -*- coding: utf-8 -*-

# External imports
import json
import re


#DataFrameExtend
class DataFrameExtend(object):
	pattern_lt = '^(\[|\()(.*)(\]|\)$)'
	pattern_clean = "\s+|'"

	def __init__(self, data_frame=None, path=None, suffix='', merge_parameters='{}'):
		self.path = path
		self.data_frame = data_frame
		self.suffix = suffix
		self.merge_parameters = json.loads(merge_parameters) if merge_parameters else {}
		self.on_in_left = DataFrameExtend.set_on_in_left(merge_parameters)
		self.on_in_right = DataFrameExtend.set_on_in_right(merge_parameters)

	@classmethod
	def set_on_in_left(clc, merge_parameters):
		return None if not merge_parameters else 'left_on' if 'left_on' in merge_parameters else 'on'

	@classmethod
	def set_on_in_right(clc, merge_parameters):
		return None if not merge_parameters else 'right_on' if 'right_on' in merge_parameters else 'on'

	@classmethod
	def check_duplicates(cls, data_frame, columns):
		shape1 = data_frame.shape
		shape2 = data_frame.drop_duplicates(columns).shape
		if shape1 == shape2:
			return True
		else:
			raise Exception(
				'DataFrameExtend:check_duplicates  --  Duplicated generated: From ' + str(shape1) +  ' to ' + str(shape2))
