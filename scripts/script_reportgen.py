# -*- coding: utf-8 -*-

# External imports
import argparse
import logging

# Internal imports (if any)
import quants.reportgen

if __name__ == '__main__':
	text_desc = 'This module let create parameterizable reports'
	parser = argparse.ArgumentParser(description=text_desc)
	parser.add_argument('config_file', help='Configuration file path')
	parser.add_argument('output_file', help='Output file path')
	args = parser.parse_args()

	quants.reportgen.WriterWrapper.xva_generate_report(args.config_file, args.output_file)