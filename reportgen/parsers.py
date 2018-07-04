# -*- coding: utf-8 -*-

# External imports
import csv
import lxml.etree
import pandas
import re
from simpledbf import Dbf5

# Internal imports (if any)
import reportgen.object_extensions


# ParserBase
class ParserBase(object):
    @classmethod
    def get_with_default(cls, value, default_value):
        return value if value else default_value

    @classmethod
    def check_extension(cls, extension):
        return extension in cls.extensions

    @classmethod
    def collect_filters(cls, file):
        filters = {}
        for filter in ParserXML.get_xpath_collection(file, col='filters/filter'):
            filters[ParserXML.get_xpath_node(filter, '@col')] = ParserXML.get_xpath_collection(filter, 'value/text()')
        return filters


# ParserCSV
class ParserCSV(ParserBase):
    extensions = ['.xls', '.csv']
    pattern_comment_line = '#.*'

    @classmethod
    def get_first_valid_row(cls, path):
        cont = 0
        with open(path, 'rb') as file:
            reader = csv.reader(file)
            for row in reader:
                if re.match(ParserCSV.pattern_comment_line, ''.join(row)):
                    cont = cont + 1
                else:
                    break
        return cont

    @classmethod
    def collect_parameters(cls, file):
        parameters = []
        parameters.append(ParserXML.get_xpath_node(file, '@path'))
        parameters.append(ParserXML.get_xpath_node(file, '@suffix'))
        parameters.append(ParserXML.get_xpath_collection(file, 'columns/column/@col'))
        parameters.append(ParserXML.get_xpath_collection(file, 'columns/column/@df_col'))
        parameters.append(ParserXML.get_xpath_node(file, 'merge_parameters/@parameters'))
        parameters.append(ParserBase.collect_filters(file))
        parameters.append(ParserBase.get_with_default(ParserXML.get_xpath_node(file, '@sep'), ','))
        parameters.append(ParserBase.get_with_default(ParserXML.get_xpath_node(file, '@enconding'), 'utf-8'))
        parameters.append(ParserBase.get_with_default(ParserXML.get_xpath_node(file, '@thousands'), ','))
        parameters.append(ParserBase.get_with_default(ParserXML.get_xpath_node(file, '@decimal'), '.'))
        return parameters

    @classmethod
    def create_df(cls, path, suffix, cols, df_cols, merge_parameters, filters, sep, enconding, thousands, decimal):
        cls._logger.info("ParserCSV:create_df -- Creating data frame " + path)
        dfe = reportgen.object_extensions.DataFrameExtend(path=path, suffix=suffix, merge_parameters=merge_parameters)
        df = pandas.read_csv(path, header=ParserCSV.get_first_valid_row(path),
            sep=sep, encoding=enconding, thousands=thousands, decimal=decimal)
        for k, v in filters.items():
            df = df.loc[(df[k].isin(v))]
        dfe.data_frame = df[cols].rename(columns=dict(zip(cols, df_cols))) if cols else df
        cls._logger.info('ParserCSV:create_df -- Created data frame ' + str(dfe.data_frame.shape))
        return dfe


# ParserXML
class ParserXML(ParserBase):
    extensions = ['.xml']

    @classmethod
    def get_xpath_collection(cls, base, col, default_value=[]):
        if base is not None:
            node = base.xpath(col)
            if not node:
                return default_value
            return node
        else:
            raise Exception('ParserXML:get_xpath_collection -- Invalid argument node_base')

    @classmethod
    def get_xpath_node(cls, base, col, default_value=None):
        collection = ParserXML.get_xpath_collection(base, col)
        return collection[0] if collection else default_value

    @classmethod
    def collect_parameters(cls, file):
        parameters = []
        parameters.append(ParserXML.get_xpath_node(file, '@path'))
        parameters.append(ParserXML.get_xpath_node(file, '@suffix'))
        parameters.append(ParserXML.get_xpath_node(file, 'columns/@base'))
        parameters.append(ParserXML.get_xpath_collection(file, 'columns/column/@col'))
        parameters.append(ParserXML.get_xpath_collection(file, 'columns/column/@df_col'))
        parameters.append(ParserXML.get_xpath_node(file, 'merge_parameters/@parameters'))
        parameters.append(ParserBase.collect_filters(file))
        return parameters

    @classmethod
    def create_df(cls, path, suffix, base, cols, df_cols, merge_parameters, filters):
        cls._logger.info("ParserXML:create_df -- Creating data frame " + path)
        rows = [[ParserXML.get_xpath_node(node, col)
                for col in cols]
                for node in ParserXML.get_xpath_collection(lxml.etree.parse(path), base)]
        dfe = reportgen.object_extensions.DataFrameExtend(path=path, suffix=suffix, merge_parameters=merge_parameters)
        df = pandas.DataFrame.from_records(rows, columns=df_cols)
        for k, v in filters.items():
            df = df.loc[(df[k].isin(v))]
        dfe.data_frame = df
        cls._logger.info('ParserXML:create_df -- Created data frame ' + str(dfe.data_frame.shape))
        return dfe


# ParserDBF
class ParserDBF(ParserBase):
    extensions = ['.dbf']

    @classmethod
    def collect_parameters(cls, file):
        parameters = []
        parameters.append(ParserXML.get_xpath_node(file, '@path'))
        parameters.append(ParserXML.get_xpath_node(file, '@path_form'))
        parameters.append(ParserXML.get_xpath_node(file, '@suffix'))
        parameters.append(ParserXML.get_xpath_collection(file, 'columns/column/@col'))
        parameters.append(ParserXML.get_xpath_collection(file, 'columns/column/@df_col'))
        parameters.append(ParserXML.get_xpath_node(file, 'merge_parameters/@parameters'))
        parameters.append(ParserBase.collect_filters(file))
        parameters.append(ParserBase.get_with_default(ParserXML.get_xpath_node(file, '@sep'), ','))
        parameters.append(ParserBase.get_with_default(ParserXML.get_xpath_node(file, '@enconding'), 'utf-8'))
        parameters.append(ParserBase.get_with_default(ParserXML.get_xpath_node(file, '@thousands'), ','))
        parameters.append(ParserBase.get_with_default(ParserXML.get_xpath_node(file, '@decimal'), '.'))
        Dbf5(parameters[0], parameters[8]).to_csv(parameters[1])
        return parameters

    @classmethod
    def create_df(cls, path, path_form, suffix, cols, df_cols, merge_parameters, filters, sep, enconding, thousands, decimal):
        cls._logger.info("ParserCSV:create_df -- Creating data frame " + path_form)
        dfe = reportgen.object_extensions.DataFrameExtend(path=path, suffix=suffix, merge_parameters=merge_parameters)
        df = pandas.read_csv(path_form, header=ParserCSV.get_first_valid_row(path_form),
                             sep=sep, encoding=enconding, thousands=thousands, decimal=decimal)
        for k, v in filters.items():
            df = df.loc[(df[k].isin(v))]
        dfe.data_frame = df[cols].rename(columns=dict(zip(cols, df_cols))) if cols else df
        print 'ParserCSV:create_df -- Created data frame ' + str(dfe.data_frame.shape)
        return dfe


# Handler
class Handler(object):
parsers = [ParserCSV, ParserXML, ParserDBF]

    @classmethod
    def get_parser(cls, extension):
        for parser in cls.parsers:
            if parser.check_extension(extension):
                return parser()
