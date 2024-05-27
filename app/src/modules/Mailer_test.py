import boto3
from modules.Mailer import Mailer
from moto import mock_aws

from_email = 'from@test.com'


@mock_aws
def test_send_email():
    """ Should successfuly send email."""

    # Arrange
    ses = boto3.client('ses', region_name='eu-west-2')
    ses.verify_email_identity(EmailAddress=from_email)

    mailer = Mailer(from_email)

    to_email = 'to@test.com'
    ses.verify_email_identity(EmailAddress=to_email)

    # Act
    res = mailer.sendEmail(to_email, 'Title', '<p>Content</p>')

    # Assert
    assert res == 200


@mock_aws
def test_dont_send_email():
    """ Shouldnt send email."""

    # Arrange
    ses = boto3.client('ses', region_name='eu-west-2')
    ses.verify_email_identity(EmailAddress=from_email)

    mailer = Mailer(from_email)

    to_email = None

    # Act
    res = mailer.sendEmail(to_email, 'Title', '<p>Content</p>')

    # Assert
    assert res == None
