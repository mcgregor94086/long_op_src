# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""

    function: send_mail(send_from, send_to, subject, message, files=[],
              server="localhost", port=587, username='', password='',
              use_tls=True)

Purpose:
    Takes STL file and makes it an attachment, and emails it to send_to
    (for example to send to Microsonic for manufacturing, we send to "Lab@microsonic-inc.com"

Parameters:

    send_from, (str): a valid email address of the scanner user  who originated the job, e.g. devops@sonautics.com
    send_to,  (str):  a valid email address (or list of email addresses) to receive this email
                      when delivering a model, this is typically of the email address of the
                      target CAD provider / manufacturer who will process the model
                             e.g. Lab@microsonic-inc.com
                      when delivering an error message this typically includes the originating scanner user and
                      devops, and might also included the CAD provider / manufacturer
    subject, (single line str): preferred reference information from sender to recipient
    message, (multi line str): the text  "body" portion of the email containing
                                       Any special instructions from sender to CAD provider or manufacturer
    files=[     (an array of filenames of files to be attached, including:
        stl_file, (filename) fully qualified file path of stl_file containing the 3D model
        manifest_xml_file, (filename) SonaData information about this scan and model in XML format
        (optional) order_pdf_file, (filename(s) zero or more text or PDF files of order information
                                   for CAD and manufacturer
    ],
    server="localhost",  (str) hostname of outbound mail server to be used to send email, typically the localhost )
    port=587, (int), typically 587, the SMTP port number of the email server listening for new mail requests
    username='', (str) the username used to connect to the mail server
    password='',  (str): a password used to connect to the mail server
    use_tls=True (boolean) True if the the email will be sent encrypted using TLS encryption.

Returns:

     status, (boolean) True if mail was successfully sent. False otherwise.
     status_message: (str)  optional string describing error status (if any) or success.

Description:

    This function marshals all the data needed to send an SMTP email including zero or more MIME
    encoded attachments.

Raises: Any errors, warnings or exceptions raised, and an explanation of what the exception means

        "Mail sent" - if successful
        "Mail failed" - if not

Usage: How this class, method, or function is accessed / called.

    send_mail(send_from, send_to, subject, message, files=[],
              server="localhost", port=587, username='', password='',
              use_tls=True)


Dependencies:  Any libraries, devices, etc. that must be present.

        smtplib  package of smtp methods
        email    package of email functions.


Testing: Things to keep in mind while testing the program. Special cases to test for.

E.g.
    Test with invalid sender email, invalid recipient email, valid email addresses, and errors in other passed
    parameters.

Warnings: Anything that might be dangerous, or a source of bugs.

    Make sure SMTP server is up and receiving requests.


Updates: Document who modified the function, when, why and how.

    E.g.
        Scott McGregor,  modified 07-Apr-2021, Initial check in.

Notes:  Anything else that developers should know about this code.


"""
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders


def send_mail(send_from, send_to, subject, message,
              files=None,
              smtp_server="smtp.dreamhost.com",
              smtp_port=465,
              smtp_username='',
              smtp_password='',
              use_tls=True):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (list[str]): to name(s)
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        smtp_server (str): mail server host name
        smtp_port (int): port number
        smtp_username (str): server auth username
        smtp_password (str): server auth password
        use_tls (bool): use TLS mode
    """
    # smtp_server = "smtp.dreamhost.com"
    # smtp_port = 465  # 465 or 587 with STARTTLS https://help.dreamhost.com/hc/en-us/articles/215612887#STARTTLS
    # smtp_username = 'orders@sonautics.com'
    # smtp_password = 'Use4SonauticsOrderDaemon'

    # commaspace = ', '
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))
    if files is not None:
        for path in files:
            part = MIMEBase('application', "octet-stream")
            with open(path, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                            'attachment; filename="{}"'.format(Path(path).name))
            msg.attach(part)

    print('send_from=', send_from)
    print('send_to=', send_to)
    print('subject=', subject)
    print('message=', message)
    print('files=', files)
    print('smtp_server=', smtp_server)
    print('smtp_port=', smtp_port)
    print('smtp_username=', smtp_username)
    print('smtp_password=', smtp_password)
    print('use_tls=', use_tls)

    smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
    smtp.login(smtp_username, smtp_password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()
    return


def main():
    """
                This file's main() is only used for testing the functions defined within this file.
    """
    send_from = 'devops@sonautics.com'
    send_to = ['scott@sonautics.com']  # Use Lab@microsonic-inc.com when in production
    subject = 'Sonascan ear impression model'
    message = 'This is just a test of the SonaScan mail system'
    stl_file = '/var/www/html/sonascan/data/uploaded/10000000e1f45394/20210417171842/photoscene' \
               '-gcvnUuRaR8RX8eRVKZbFH9r7ly2AuRHpwYO3j1G1sJ0/cropped_result.stl '
    manifest_xml_file = '/home/pi/PycharmProjects/pythonProject2/sonascan-pi/src/server/manifest.xml'
    order_pdf_file = '/home/pi/PycharmProjects/pythonProject2/sonascan-pi/templates/Microsonic-Hearing-Protection' \
                     '-Order-Form-Fillable.pdf '
    attached_files = [stl_file, manifest_xml_file, order_pdf_file]
    smtp_server = "smtp.dreamhost.com"
    smtp_port = 465  # 465 or 587 with STARTTLS https://help.dreamhost.com/hc/en-us/articles/215612887#STARTTLS
    smtp_username = 'orders@sonautics.com'
    smtp_password = 'Use4SonauticsOrderDaemon'

    send_mail(send_from,
              send_to,
              subject,
              message,
              files=attached_files,
              smtp_server=smtp_server, smtp_port=smtp_port,
              smtp_username=smtp_username,  smtp_password=smtp_password, use_tls=True)


if __name__ == "__main__":  # execute only if run as a script
    main()
