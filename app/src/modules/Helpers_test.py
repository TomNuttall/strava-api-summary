import Helpers as Helpers


def test_date_ordinal_short():
    """ Should test adding ordinal to date."""

    # Arrange
    val = '21'

    # Act
    res = Helpers.date_ordinal(val)

    # Assert
    assert res == "21st"


def test_date_ordinal_long():
    """ Should test adding ordinal to date and keeping string."""

    # Arrange
    val = '21 May 2024'

    # Act
    res = Helpers.date_ordinal(val)

    # Assert
    assert res == "21st May 2024"
