from gmail import GMail, Message

# Set up emailer
gmail = GMail('TankTemp <wytamma@gmail.com>', EMAIL_PASSWORD)


def email(msgSubject, msgText, Email):
    """Sends msgText to Email"""
    msg = Message(
        msgSubject,
        to='%s <%s>' % (Email, Email),
        text=msgText
        )
    gmail.send(msg)


def mode_average(listof3):
    delta = max(listof3)
    for i, temp in enumerate(l):
        vals = l[:i] + l[i+1:]
        for j in vals:
            if abs(temp - j) > delta:
                continue
            delta = abs(temp - j)
            mode = (temp + j)/2
    return mode
