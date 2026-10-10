import os
import sys

import pymysql

pymysql.install_as_MySQLdb()


def main():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "credit_system.settings",
    )

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()