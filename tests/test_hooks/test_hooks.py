# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest.mock import MagicMock, Mock

from sceptre.hooks import (
    Hook,
    HookProperty,
    add_stack_hooks,
    execute_hooks,
    add_stack_hooks_with_aliases,
)
from sceptre.resolvers import Resolver
from sceptre.stack import Stack
import logging


class MockHook(Hook):
    def run(self):
        pass


class TestHooksFunctions(object):
    def setup_method(self, test_method):
        pass

    def test_add_stack_hooks(self):
        mock_hook_before = MagicMock(spec=Hook)
        mock_hook_after = MagicMock(spec=Hook)
        mock_object = MagicMock()

        mock_object.stack.hooks = {
            "before_mock_function": [mock_hook_before],
            "after_mock_function": [mock_hook_after],
        }

        def mock_function(self):
            assert mock_hook_before.run.call_count == 1
            assert mock_hook_after.run.call_count == 0

        mock_object.mock_function = mock_function
        mock_object.mock_function.__name__ = "mock_function"

        add_stack_hooks(mock_object.mock_function)(mock_object)

        assert mock_hook_before.run.call_count == 1
        assert mock_hook_after.run.call_count == 1

    def test_add_stack_hooks_with_aliases(self):
        mock_before_something = MagicMock(Hook)
        mock_after_something = MagicMock(Hook)
        mock_object = MagicMock()

        mock_object.stack.hooks = {
            "before_something": [mock_before_something],
            "after_something": [mock_after_something],
        }

        @add_stack_hooks_with_aliases(["something"])
        def mock_function(self):
            return 123

        mock_object.mock_function = mock_function
        mock_object.mock_function.__name__ = "mock_function"

        result = mock_function(mock_object)

        assert mock_before_something.run.call_count == 1
        assert mock_after_something.run.call_count == 1
        assert result == 123

    def test_execute_hooks_with_not_a_list(self):
        execute_hooks(None)

    def test_execute_hooks_with_empty_list(self):
        execute_hooks([])

    def test_execute_hooks_with_list_with_non_hook_objects(self):
        execute_hooks([None, "string", 1, True])

    def test_execute_hooks_with_single_hook(self):
        hook = MagicMock(spec=Hook)
        execute_hooks([hook])
        hook.run.called_once_with()

    def test_execute_hooks_with_multiple_hook(self):
        hook_1 = MagicMock(spec=Hook)
        hook_2 = MagicMock(spec=Hook)
        execute_hooks([hook_1, hook_2])
        hook_1.run.called_once_with()
        hook_2.run.called_once_with()


class MyResolver(Resolver):
    def resolve(self):
        return self.argument


class TestHook(TestCase):
    def setUp(self):
        self.stack = Mock(Stack)
        self.stack.name = "my/stack"
        self.hook = MockHook(stack=self.stack)

    def test_logger__logs_have_stack_name_prefix(self):
        with self.assertLogs(self.hook.logger.name, logging.INFO) as handler:
            self.hook.logger.info("Bonjour")

        assert handler.records[0].message == f"{self.stack.name} - Bonjour"

    def test_argument__supports_resolvers_in_arguments(self):
        arg = [MyResolver("hello")]
        hook = MockHook(arg, self.stack)
        self.assertEqual(["hello"], hook.argument)


class MockClass(object):
    hook_property = HookProperty("hook_property")
    config = MagicMock()
    name = "my/stack.yaml"


class TestHookPropertyDescriptor(object):
    def setup_method(self, test_method):
        self.mock_object = MockClass()

    def test_setting_hook_property(self):
        mock_hook = MagicMock(spec=MockHook)

        self.mock_object.hook_property = [mock_hook]
        assert self.mock_object._hook_property == [
            mock_hook.clone_for_stack.return_value
        ]

    def test_getting_hook_property(self):
        self.mock_object._hook_property = self.mock_object
        assert self.mock_object.hook_property == self.mock_object
