import boto3


class Mailer:

    def __init__(self, from_address: str):
        """ Setup ses and from address."""

        self.ses = boto3.client('ses', region_name='eu-west-2')
        self.from_address = from_address

    def sendEmail(self, to_address: str, title: str, content: dict):
        """ Use SES to send email."""

        if not to_address or not self.from_address:
            return

        res = self.ses.send_email(
            Destination={'ToAddresses': [to_address]},
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': content,
                    }
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': title,
                },
            },
            Source=self.from_address)

        return res['ResponseMetadata']['HTTPStatusCode']
