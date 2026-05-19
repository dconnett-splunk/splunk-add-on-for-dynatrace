from package.bin import dynatrace_entity_selectors as selectors
from unittest import TestCase


class Helper:
    def __init__(self, args):
        self.args = args

    def get_arg(self, field):
        if field not in self.args:
            raise KeyError(field)
        return self.args[field]


class TestDynatraceEntitySelectors(TestCase):
    def test_select_entity_types_reads_current_multiple_select_delimiter(self):
        self.assertEqual(
            ["HOST", "SERVICE", "APPLICATION"],
            selectors.select_entity_types("HOST~SERVICE~APPLICATION"),
        )

    def test_select_entity_types_falls_back_to_compatibility_textarea_value(self):
        self.assertEqual(
            ["HOST", "PROCESS_GROUP_INSTANCE", "SERVICE"],
            selectors.select_entity_types(
                "",
                "HOST, PROCESS_GROUP_INSTANCE\nSERVICE",
            ),
        )

    def test_select_entity_types_prefers_current_value_over_compatibility_value(self):
        self.assertEqual(
            ["HOST", "SERVICE"],
            selectors.select_entity_types(
                "HOST~SERVICE",
                "APPLICATION,PROCESS_GROUP",
            ),
        )

    def test_get_selected_entity_types_tolerates_missing_optional_fields(self):
        helper = Helper(
            {
                selectors.COMPATIBILITY_ENTITY_SELECTOR_TEXTAREA_FIELD: (
                    "HOST,PROCESS_GROUP_INSTANCE,PROCESS_GROUP"
                )
            }
        )

        self.assertEqual(
            [
                "HOST",
                "PROCESS_GROUP_INSTANCE",
                "PROCESS_GROUP",
            ],
            selectors.get_selected_entity_types(helper),
        )
