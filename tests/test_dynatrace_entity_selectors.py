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
    def test_select_entity_types_reads_comma_delimited_values(self):
        self.assertEqual(
            ["HOST", "SERVICE", "APPLICATION"],
            selectors.select_entity_types("HOST,SERVICE,APPLICATION"),
        )

    def test_select_entity_types_handles_newlines_and_spaces(self):
        self.assertEqual(
            ["HOST", "PROCESS_GROUP_INSTANCE", "SERVICE"],
            selectors.select_entity_types("HOST, PROCESS_GROUP_INSTANCE\nSERVICE"),
        )

    def test_get_selected_entity_types_reads_canonical_ucc_field(self):
        helper = Helper(
            {
                selectors.ENTITY_SELECTOR_FIELD: (
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

    def test_get_selected_entity_types_tolerates_missing_optional_field(self):
        self.assertEqual([], selectors.get_selected_entity_types(Helper({})))
