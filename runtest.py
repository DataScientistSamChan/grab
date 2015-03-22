#!/usr/bin/env python
# coding: utf-8
import unittest
import sys
from optparse import OptionParser
import logging
from copy import copy

from test.util import prepare_test_environment, clear_test_environment, GLOBAL
from tools.watch import watch

# **********
# Grab Tests
# * pycurl transport
# * extensions
# **********
GRAB_TEST_LIST = (
    # Internal API
    'test.grab_api',
    'test.grab_transport',
    'test.response_class',
    'test.grab_debug',
    # Response processing
    'test.grab_xml_processing',
    'test.grab_response_body_processing',
    'test.grab_charset',
    # Network
    'test.grab_get_request',
    'test.grab_post_request',
    'test.grab_request',
    'test.grab_user_agent',
    'test.grab_cookies',
    # Refactor
    'test.grab_proxy',
    'test.grab_upload_file',
    'test.grab_limit_option',
    'test.grab_charset_issue',
    'test.grab_pickle',
    # *** Extension sub-system
    'test.extension',
    # *** Extensions
    'test.ext_text',
    'test.ext_rex',
    'test.ext_lxml',
    #'test.ext_form',
    'test.ext_doc',
    'test.ext_structured',
    # *** Pycurl Test
    'test.pycurl_cookie',
    # *** util.module
    'test.util_module',
    'test.util_log',
    # *** grab.export
    'test.export_mysql_dumper',
)

GRAB_EXTRA_TEST_LIST = (
    'test.grab_django',
    'test.ext_pyquery',
    'test.item_deprecated',
    'test.tools_deprecated',
)

# ************
# Spider Tests
# ************

SPIDER_TEST_LIST = (
    'test.spider',
    #'tests.test_distributed_spider',
    'test.spider_task',
    'test.spider_proxy',
    'test.spider_queue',
    'test.spider_misc',
    'test.spider_meta',
    'test.spider_error',
    'test.spider_cache',
)

SPIDER_EXTRA_TEST_LIST = ()


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = OptionParser()
    parser.add_option('-t', '--test', help='Run only specified tests')
    parser.add_option('--transport', help='Test specified transport',
                      default='grab.transport.curl.CurlTransport')
    parser.add_option('--extra', action='store_true',
                      default=False, help='Run extra tests for specific backends')
    parser.add_option('--test-grab', action='store_true',
                      default=False, help='Run tests for Grab::Spider')
    parser.add_option('--test-spider', action='store_true',
                      default=False, help='Run tests for Grab')
    parser.add_option('--test-all', action='store_true',
                      default=False, help='Run tests for both Grab and Grab::Spider')
    parser.add_option('--backend-mongo', action='store_true',
                      default=False, help='Run extra tests that depends on mongodb')
    parser.add_option('--backend-redis', action='store_true',
                      default=False, help='Run extra tests that depends on redis')
    parser.add_option('--backend-mysql', action='store_true',
                      default=False, help='Run extra tests that depends on mysql')
    parser.add_option('--backend-postgresql', action='store_true',
                      default=False, help='Run extra tests that depends on postgresql')
    opts, args = parser.parse_args()

    GLOBAL['transport'] = opts.transport

    if opts.backend_mongo:
        GLOBAL['backends'].append('mongo')

    if opts.backend_redis:
        GLOBAL['backends'].append('redis')

    if opts.backend_mysql:
        GLOBAL['backends'].append('mysql')

    if opts.backend_postgresql:
        GLOBAL['backends'].append('postgresql')

    prepare_test_environment()
    test_list = []

    if opts.test_all:
        test_list += GRAB_TEST_LIST
        test_list += SPIDER_TEST_LIST
        if opts.extra:
            test_list += GRAB_EXTRA_TEST_LIST
            test_list += SPIDER_EXTRA_TEST_LIST

    if opts.test_grab:
        test_list += GRAB_TEST_LIST
        if opts.extra:
            test_list += GRAB_EXTRA_TEST_LIST

    if opts.test_spider:
        test_list += SPIDER_TEST_LIST
        if opts.extra:
            test_list += SPIDER_EXTRA_TEST_LIST

    if opts.test:
        test_list += [opts.test]

    # Check tests integrity
    # Ensure that all test modules are imported correctly
    for path in test_list:
        __import__(path, None, None, ['foo'])

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for path in test_list:
        mod_suite = loader.loadTestsFromName(path)
        for some_suite in mod_suite:
            for test in some_suite:
                if not hasattr(test, '_backend') or test._backend in GLOBAL['backends']:
                    suite.addTest(test)

    runner = unittest.TextTestRunner()

    result = runner.run(suite)

    clear_test_environment()
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
