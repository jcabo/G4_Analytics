# -*- coding: utf-8 -*-

# External imports
import collections
import json
import lxml.etree
import os
import pandas

# Internal imports (if any)
import reportgen.helper_conf_wrapper
import reportgen.object_extensions
import reportgen.parsers


#ReduceBinaryOp
class ReduceBinaryOp(object):
    def __init__(self, func):
		self.func = func

    def __call__(self, arg, **kwargs):
		if len(arg) == 0:
			return None
		elif len(arg) == 1:
			return arg[0]
		elif len(arg) == 2:
			return self.func(arg[0], arg[1], **kwargs)
		else:
			return self.func(ReduceBinaryOp(self.func)(arg[:len(arg) - 1], **kwargs),
							 arg[len(arg) - 1], **kwargs)


#IReport
class IReport(object):
	@classmethod
	def create_df(cls, file):
		print 'IReport:create_df -- Creating data frame'
		parser = reportgen.parsers.Handler.get_parser(os.path.splitext(reportgen.parsers.ParserXML.get_xpath_node(file, '@path'))[1])
		df = parser.create_df(*parser.collect_parameters(file))
		df.data_frame.select_dtypes(include=['object']).apply(lambda x: str(x).strip())
		return df

	@classmethod
	def create_dfs(cls, xtree, xpath_files):
		print 'IReport:create_dfs -- Creating data frames'
		files = reportgen.parsers.ParserXML.get_xpath_collection(xtree, xpath_files)
		dfs = collections.OrderedDict()
		for df in [IReport.create_df(file) for file in files]:
			dfs[df.suffix] = df
		return dfs

	@classmethod
	def merge(cls, df1, df2):
		print 'IReporprint t:merge -- Merging data frames: '
		print 'IReport:merge -- Data frame ' + df1.suffix + ': ' + str(df1.data_frame.shape)
		print 'IReport:merge -- Data frame ' + df2.suffix + ': ' + str(df2.data_frame.shape)
		for df, on in [[df1, df1.on_in_left], [df2, df1.on_in_right]]:
			df_col = [col for col in df.data_frame.columns.values.tolist() if col not in df1.merge_parameters[on]]
			df_col_format = [col + df.suffix for col in df_col]
			df.data_frame.rename(columns=dict(zip(df_col, df_col_format)), inplace=True)
		print 'IReport:merge -- Merge_parameters' + json.dumps(df1.merge_parameters)
		df = pandas.merge(df1.data_frame, df2.data_frame, **df1.merge_parameters)
		dfe = reportgen.object_extensions.DataFrameExtend(data_frame=df, merge_parameters=json.dumps(df2.merge_parameters))
		print 'IReport:merge -- Merged data frames ' + str(dfe.data_frame.shape)
		return dfe


#WriterWrapper
class WriterWrapper(object):
	@classmethod
	def xva_generate_report(cls, config_file, output_file, args_output={'index': False, 'sep': ',', 'encoding': 'utf-8'}):
		dfs = IReport.create_dfs(lxml.etree.parse(config_file), reportgen.helper_conf_wrapper.HelperConfigurationWrapper.xpath_files)
		func = lambda df1, df2: IReport.merge(df1, df2)
		df = ReduceBinaryOp(func)(dfs.values())
		df.data_frame.to_csv(output_file, **args_output)