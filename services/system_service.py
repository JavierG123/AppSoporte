from typing import List, Sequence


def get_installed_apps() -> List[str]:
    """Return installed application names from local machine."""
    import winapps

    return [app.name for app in winapps.list_installed()]


def compare_apps(expected_programs: Sequence[str], installed_apps: Sequence[str]) -> List[str]:
    """Compare expected programs against installed apps and return missing ones."""
    missing_apps: List[str] = []
    for program_name in expected_programs:
        if not any(program_name in app_name for app_name in installed_apps):
            missing_apps.append(program_name)
    return missing_apps
