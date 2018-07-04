# -*- coding: utf-8 -*-

# External imports
from datetime import datetime
import functools
import glob
import lxml.etree
import re

# Internal imports (if any)
import reportgen.parsers


# HelperConfigurationWrapper
class HelperConfigurationWrapper(object):

    xpath_files = '/configuration/files/file'
    pattern_db_date = '^(.*)(\\\\)(\d{8})(\\\\)(.*)$'
    pattern_valid_date = '^\d{8}$'

    @classmethod
    def convert_dateformatstr2ordinal(cls, date, format='%Y%m%d'):
        return datetime.strptime(date, format).toordinal() - 693594

    @classmethod
    def convert_ordinal2dateformatstr(cls, date, format='%Y%m%d'):
        return datetime.fromordinal(datetime(1900, 1, 1).toordinal() + date - 2).strftime(format)

    @classmethod
    def get_dirs_matched(cls, pattern_path, pattern_re='.*', group=0):
        return [match.group(group) for match in [
                re.match(pattern_re, path_matched) for path_matched in [
                    path for path in glob.glob(pattern_path)]]
               if match]

    @classmethod
    def select_date(cls, xtree, suffixes):
        #excepcion si ninguna ruta cumple el patron
        patterns_db_path = [reportgen.parsers.ParserXML.get_xpath_node(xtree, HelperConfigurationWrapper.xpath_files +
                            "[@suffix='" + suffix + "']/root_db_path/@path") + \
                            '\\*\\' + \
                            reportgen.parsers.ParserXML.get_xpath_node(xtree, HelperConfigurationWrapper.xpath_files +
                            "[@suffix='" + suffix + "']/ct_path/@path")
                            for suffix in suffixes]
        dates = [sorted(HelperConfigurationWrapper.get_dirs_matched(pattern_db_path,
            pattern_re=HelperConfigurationWrapper.pattern_db_date, group=3))
            for pattern_db_path in patterns_db_path]
        dates = set.intersection(*[set(i) for i in dates])
        if not dates:
            raise Exception('HelperConfigurationWrapper:select_date  --  Any path match pattern ' + pattern_db_path)

        print ''
        print 'Select one of this dates: '
        for date in dates:
            print date
        date = raw_input('Date: ')
        if not re.match(HelperConfigurationWrapper.pattern_valid_date, date) and date:
            HelperConfigurationWrapper.select_date(xtree)
        print ''
        return date

    @classmethod
    def get_path(cls, xtree, suffix):
        # excepcion si no existen los tag en el xml
		root_db_path = reportgen.parsers.ParserXML.get_xpath_node(xtree,
            HelperConfigurationWrapper.xpath_files + "[@suffix='" + suffix + "']/root_db_path/@path")
		ct_path = reportgen.parsers.ParserXML.get_xpath_node(xtree,
            HelperConfigurationWrapper.xpath_files + "[@suffix='" + suffix + "']/ct_path/@path")
		return [root_db_path, ct_path]

    @classmethod
    def get_path_db(cls, xtree, suffix, date):
        if re.match(HelperConfigurationWrapper.pattern_valid_date, date):
            root_db_path, ct_path = HelperConfigurationWrapper.get_path(xtree, suffix)
            return '\\'.join([root_db_path, date, ct_path])
        else:
            raise Exception('HelperConfigurationWrapper:get_path_db  --  Invalid date ' + date +
                '. Not match pattern ' + HelperConfigurationWrapper.pattern_valid_date)

    @classmethod
    def get_path_dr_snapshot(cls, xtree, suffix, date, snapshot):
        if re.match(HelperConfigurationWrapper.pattern_valid_date, date):
            root_db_path, ct_path = HelperConfigurationWrapper.get_path(xtree, suffix)
            return root_db_path + "\\day" + date + "\\BBVA_" + snapshot + "_SIM" + "\\BBVA_" + snapshot + ".FOL." + ct_path
        else:
            raise Exception('HelperConfigurationWrapper:get_path_dr_snapshot  --  Invalid date ' + date +
                '. Not match pattern ' + HelperConfigurationWrapper.pattern_valid_date)

    @classmethod
    def get_path_dr(cls, xtree, suffix, date):
        if re.match(HelperConfigurationWrapper.pattern_valid_date, date):
            root_db_path, ct_path = HelperConfigurationWrapper.get_path(xtree, suffix)
            return root_db_path + "\\day" + date + "\\" + ct_path
        else:
            raise Exception('HelperConfigurationWrapper:get_path_dr  --  Invalid date ' + date +
                '. Not match pattern ' + HelperConfigurationWrapper.pattern_valid_date)

    @classmethod
    def set_path(cls, xtree, suffix, path):
        if path:
            reportgen.parsers.ParserXML.get_xpath_node(
                xtree, HelperConfigurationWrapper.xpath_files + "[@suffix='" + suffix + "']").attrib['path'] = path
        else:
            raise Exception('HelperConfigurationWrapper:set_path  --  Empty path')

    @classmethod
    def set_filters(cls, xtree, suffix, filters):
        if filters:
            file = reportgen.parsers.ParserXML.get_xpath_node(xtree, HelperConfigurationWrapper.xpath_files + "[@suffix='" + suffix + "']")
            node_filters = lxml.etree.SubElement(file, 'filters')
            for k, v in filters.items():
                node_filter = lxml.etree.SubElement(node_filters, 'filter', attrib={'col': k})
                for value in v:
                    node_value = lxml.etree.SubElement(node_filter, 'value')
                    node_value.text = str(value)
