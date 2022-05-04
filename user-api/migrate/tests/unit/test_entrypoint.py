import entrypoint


def test_run_migrations_exists():
    """Test entrypoint succesfully imported."""
    assert entrypoint.run_migrations is not None
