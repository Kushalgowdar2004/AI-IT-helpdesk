from sqlalchemy.orm import Session
from .models import KBArticle

SEED_ARTICLES = [
    dict(
        id='KB-1001', category='Network',
        title='VPN drops repeatedly after a Windows update',
        body="Windows updates sometimes reset the network adapter's power management settings, causing the VPN client to disconnect every few minutes. Fix: open Device Manager, find the network adapter, open Properties > Power Management, and uncheck 'Allow the computer to turn off this device to save power'. Then restart the VPN client. If it persists, roll back the adapter driver.",
    ),
    dict(
        id='KB-1002', category='Network',
        title='Cannot connect to office WiFi on a new device',
        body="New devices need to be added to the MAC allowlist for the corporate SSID. Confirm you're using 'Corp-Secure' not 'Corp-Guest', forget the network and rejoin with your SSO credentials, and check that the device's WiFi driver is up to date.",
    ),
    dict(
        id='KB-1003', category='Network',
        title='Slow internet speeds on company laptop',
        body="Run a speed test on ethernet vs WiFi to isolate whether it's the WiFi adapter, the router, or the ISP. Disable any VPN split-tunneling misconfiguration, close background sync clients (cloud storage), and check for firmware updates on the office router.",
    ),
    dict(
        id='KB-1004', category='Hardware',
        title='External monitor not detected after docking',
        body="Reseat the dock's display cable, and confirm the monitor is on the correct input. On Windows, press Win+P and select 'Extend'. On macOS, hold Option while clicking Detect Displays in System Settings > Displays. If the dock uses DisplayLink, reinstall the DisplayLink driver.",
    ),
    dict(
        id='KB-1005', category='Hardware',
        title='Laptop battery draining unusually fast',
        body='Check Activity Monitor / Task Manager for a runaway process pinning the CPU. Disable unnecessary startup apps, lower screen brightness, and check battery health in system settings — anything under 80% health after 2 years is normal wear, but a sudden drop suggests a battery replacement is due.',
    ),
    dict(
        id='KB-1006', category='Hardware',
        title='Printer shows offline despite being powered on',
        body="Remove and re-add the printer from the OS print queue, confirm it's on the same subnet as your machine, and restart the print spooler service (Windows) or reset the printing system (macOS: right-click the printer list, 'Reset printing system').",
    ),
    dict(
        id='KB-1007', category='Software',
        title='Application crashes on launch after an update',
        body="Clear the app's cache/local config folder, confirm you're on the latest patch (not just the latest major version), and check for conflicting background software like antivirus intercepting the app's process. Reinstalling is a last resort — back up local settings first.",
    ),
    dict(
        id='KB-1008', category='Software',
        title='Software license shows as expired or invalid',
        body="Licenses are pooled centrally and renew automatically, but a stale local cache can show a false expiry. Sign out and back into the license manager, confirm your seat wasn't reassigned, and check system clock accuracy — a wrong local date will falsely invalidate time-bound licenses.",
    ),
    dict(
        id='KB-1009', category='Access & Accounts',
        title='Locked out of account after failed login attempts',
        body="Accounts lock for 15 minutes after 5 failed attempts as a brute-force protection. Wait it out or use the self-service unlock portal with SSO verification. If MFA is failing, resync the authenticator app's time or request a backup code from IT.",
    ),
    dict(
        id='KB-1010', category='Access & Accounts',
        title='Cannot access a shared drive or folder',
        body="Confirm group membership in the identity portal — access is granted via group, not per-user. Requests typically take up to 30 minutes to propagate. If it's been longer, the request may need re-approval from the resource owner.",
    ),
    dict(
        id='KB-1011', category='Email & Collaboration',
        title='Not receiving external emails',
        body="Check the spam/quarantine folder in the mail security gateway first — most 'missing' external mail is quarantined, not lost. Confirm the sender's domain isn't on a blocklist, and check mailbox storage isn't full.",
    ),
    dict(
        id='KB-1012', category='Email & Collaboration',
        title='Video calls freezing or dropping in meetings',
        body="Switch from WiFi to ethernet if possible, disable incoming video to reduce bandwidth, and close other bandwidth-heavy apps (cloud backups, streaming). If it's isolated to one platform, clear that app's cache or try the browser version instead of the native client.",
    ),
    dict(
        id='KB-1013', category='Access & Accounts',
        title='Forgot password or password reset needed',
        body='Use the company self-service password reset portal and complete identity verification. Choose a new password that meets the organization policy. If self-service reset fails, submit an access ticket to IT.',
    ),
    dict(
        id='KB-1014', category='Access & Accounts',
        title='MFA push notification not received',
        body='Check that the authenticator app has notifications enabled and the phone has network access. Open the authenticator app manually and look for a pending approval. If the device was replaced or lost, request an MFA reset from IT.',
    ),
    dict(
        id='KB-1015', category='Access & Accounts',
        title='MFA code rejected or authenticator out of sync',
        body='Confirm the phone date and time are set automatically. Generate a fresh code and retry rather than reusing an expired code. If codes continue to fail, ask IT to resync or reset the authenticator registration.',
    ),
    dict(
        id='KB-1016', category='Access & Accounts',
        title='Application access request or permission missing',
        body='Confirm the exact application and business purpose. Request access through the identity/access portal and select the appropriate group or role. Access requiring manager or resource-owner approval may remain pending until approved.',
    ),
    dict(
        id='KB-1017', category='Access & Accounts',
        title='Company portal or SSO login failure',
        body='Confirm the company account is active and try the SSO sign-in again in a private browser window. Clear stale browser credentials if the login loops. If other employees are also affected, submit an access incident to IT.',
    ),
    dict(
        id='KB-1018', category='Access & Accounts',
        title='Shared folder access request still pending',
        body='Check the request status in the identity portal and confirm the correct group was requested. Allow the normal propagation window after approval. If access is still missing, ask the resource owner or IT to re-approve the group membership.',
    ),
    dict(
        id='KB-1019', category='Network',
        title='VPN authentication failed',
        body='Confirm the corporate username and password are current and that MFA approval is completed. Disconnect other VPN clients and retry from a stable internet connection. If authentication continues to fail, submit a VPN access ticket with the exact error.',
    ),
    dict(
        id='KB-1020', category='Network',
        title='Connected to WiFi but websites do not open',
        body='Confirm the device received an IP address and try another internal or public site. Temporarily disconnect from VPN and retry to isolate whether the VPN is involved. If only one network has the issue, reconnect to the corporate SSID and contact IT if it persists.',
    ),
    dict(
        id='KB-1021', category='Network',
        title='Ethernet connection not working',
        body='Reseat the Ethernet cable and check whether the dock or wall port shows link activity. Try a known-good cable or another port if available. If WiFi works but Ethernet does not, provide IT with the device and port details.',
    ),
    dict(
        id='KB-1022', category='Network',
        title='Network connection drops intermittently',
        body='Note whether the drops occur on WiFi, Ethernet, or VPN. Move closer to the access point for WiFi testing and compare with Ethernet if possible. Record the approximate times and error messages for IT if the issue continues.',
    ),
    dict(
        id='KB-1023', category='Network',
        title='Cannot access an internal company website',
        body='Confirm you are connected to the corporate network or VPN. Check whether other internal sites work to determine if the issue is site-specific. If the site alone fails, provide IT with the URL and exact browser error.',
    ),
    dict(
        id='KB-1024', category='Network',
        title='DNS or name resolution problem',
        body='Test whether the issue affects multiple websites and whether direct IP access behaves differently. Disconnect and reconnect the network connection, then retry. If several employees have the same issue, escalate it as a possible network/DNS incident.',
    ),
    dict(
        id='KB-1025', category='Hardware',
        title='Laptop will not turn on',
        body='Connect the laptop to AC power and check for charging indicators. Disconnect nonessential peripherals and try a normal power-on again. If there are no lights or response after charging, contact hardware support rather than repeatedly forcing power cycles.',
    ),
    dict(
        id='KB-1026', category='Hardware',
        title='Laptop is not charging',
        body='Check that the charger is firmly connected at both ends and test another compatible power outlet. Inspect the cable and connector for visible damage. If the laptop runs on battery but does not charge with a known-good adapter, request hardware support.',
    ),
    dict(
        id='KB-1027', category='Hardware',
        title='Keyboard not working',
        body='Reconnect the keyboard or docking connection and test another USB port if applicable. For a laptop keyboard, restart the device and test a few keys after login. If an external keyboard works but the built-in keyboard does not, submit a hardware ticket.',
    ),
    dict(
        id='KB-1028', category='Hardware',
        title='Mouse or trackpad not working',
        body='Reconnect the mouse or receiver and check its battery if it is wireless. Test another USB port or a known-good mouse. For a trackpad issue, restart the laptop and verify the pointing device is enabled in system settings.',
    ),
    dict(
        id='KB-1029', category='Hardware',
        title='Webcam not detected',
        body='Check the physical privacy shutter and confirm camera permissions are enabled for the meeting application. Close other applications that may be using the camera and retry. If the camera is missing from system settings, submit a hardware ticket.',
    ),
    dict(
        id='KB-1030', category='Hardware',
        title='Microphone not detected',
        body='Check the mute switch and confirm the correct input device is selected in the operating system and meeting application. Test the microphone in system settings. If another microphone works but the built-in device does not, contact IT.',
    ),
    dict(
        id='KB-1031', category='Hardware',
        title='Docking station not working',
        body='Disconnect the dock from power and the laptop, wait briefly, then reconnect power followed by the laptop connection. Reseat display, USB, and network cables. If only one dock or port fails, provide IT with the dock model and affected port.',
    ),
    dict(
        id='KB-1032', category='Hardware',
        title='USB device not recognized',
        body='Disconnect and reconnect the USB device and try another port. If possible, test the device on another computer to isolate the device from the laptop. Avoid using damaged cables or devices and contact IT if the device remains unrecognized.',
    ),
    dict(
        id='KB-1033', category='Windows & OS',
        title='Windows laptop is very slow',
        body='Open Task Manager and check CPU, memory, and disk usage for an unusually high process. Close unnecessary applications and restart the laptop. If performance remains poor, note the resource usage and submit a performance ticket.',
    ),
    dict(
        id='KB-1034', category='Windows & OS',
        title='Windows update is stuck',
        body='Keep the laptop connected to power and a stable network while checking the update status. Restart only if Windows explicitly offers a restart or the update has clearly stalled according to company guidance. If the device repeatedly fails updates, provide the update error code to IT.',
    ),
    dict(
        id='KB-1035', category='Windows & OS',
        title='Laptop freezes or becomes unresponsive',
        body='Wait briefly to see whether the application recovers, then try Task Manager to identify a hung application. If the whole system is unresponsive, restart using the normal Windows restart process when possible. Record what application was running before the freeze.',
    ),
    dict(
        id='KB-1036', category='Windows & OS',
        title='Blue screen or unexpected system crash',
        body='Record the stop code and approximate time of the crash. Disconnect recently added peripherals and check whether the crash repeats after a normal restart. Repeated blue screens should be escalated with the stop code and recent software or hardware changes.',
    ),
    dict(
        id='KB-1037', category='Windows & OS',
        title='Windows does not boot normally',
        body='Disconnect nonessential USB devices and retry a normal startup. If Windows enters recovery, use the available startup repair options according to company policy. If recovery fails or important data may be at risk, stop troubleshooting and contact IT.',
    ),
    dict(
        id='KB-1038', category='Software',
        title='Software will not install',
        body='Confirm the application is approved and that the installer matches the operating system. Check available disk space and whether the installation requires elevated permissions. If installation is managed centrally, request deployment through the approved software portal.',
    ),
    dict(
        id='KB-1039', category='Software',
        title='Outdated application needs an update',
        body='Check the approved software portal or application update mechanism for the latest supported version. Save work before restarting the application. If the update is blocked by policy or fails repeatedly, provide the version and error message to IT.',
    ),
    dict(
        id='KB-1040', category='Software',
        title='Application is extremely slow',
        body='Restart the application and check whether the slowdown affects only one program. Close unnecessary background applications and verify available memory and disk space. If the issue began after an update, include the version and timing in the support ticket.',
    ),
    dict(
        id='KB-1041', category='Software',
        title='Browser pages or web application not loading correctly',
        body="Refresh the page and test the same site in a private window or another supported browser. Clear the affected site's cache if appropriate and disable problematic extensions for testing. If only a corporate application fails, provide the URL and browser error to IT.",
    ),
    dict(
        id='KB-1042', category='Email & Collaboration',
        title='Outlook will not open',
        body='Restart Outlook and confirm the device has network access. If Outlook remains stuck, try the supported webmail client to determine whether the account itself is available. If webmail works but desktop Outlook does not, submit an Outlook support ticket.',
    ),
    dict(
        id='KB-1043', category='Email & Collaboration',
        title='Emails are stuck in Outlook Outbox',
        body='Confirm network connectivity and open the Outbox to identify the affected message. Remove oversized attachments or retry after reconnecting to the network. If messages remain stuck, use webmail temporarily and provide IT with the error.',
    ),
    dict(
        id='KB-1044', category='Email & Collaboration',
        title='Mailbox is full',
        body='Review large messages and attachments and archive or delete items according to company retention policy. Empty deleted items only when permitted by policy. If the mailbox remains full because of a retention requirement, contact IT for mailbox management.',
    ),
    dict(
        id='KB-1045', category='Email & Collaboration',
        title='Teams microphone or camera not working',
        body='Open Teams device settings and select the intended microphone and camera. Check operating-system privacy permissions and close other applications using the devices. Run a test call before joining the meeting again.',
    ),
    dict(
        id='KB-1046', category='Email & Collaboration',
        title='Teams will not open or keeps crashing',
        body='Restart Teams and verify the network connection. Install the approved current version or use the supported web client as a temporary workaround. If the problem persists after an update, submit the Teams version and error details to IT.',
    ),
    dict(
        id='KB-1047', category='Email & Collaboration',
        title='Calendar is not syncing',
        body='Confirm the device has network connectivity and that the correct work account is signed in. Compare the desktop calendar with webmail to determine whether the issue is local or account-wide. If webmail is correct but the desktop client is stale, restart the client and submit a ticket if it continues.',
    ),
    dict(
        id='KB-1048', category='Security',
        title='Received a suspicious or phishing email',
        body='Do not click links, open unexpected attachments, or reply with credentials. Use the company phishing-reporting mechanism if available and delete or quarantine the message according to policy. If you already clicked a link or entered credentials, report it to IT/security immediately.',
    ),
    dict(
        id='KB-1049', category='Security',
        title='Clicked a suspicious link or attachment',
        body='Stop interacting with the message and do not enter additional credentials. Disconnect from sensitive sessions if instructed by company security procedures and report the incident immediately. Tell IT/security what was clicked and whether credentials or files were entered or downloaded.',
    ),
    dict(
        id='KB-1050', category='Security',
        title='Company laptop lost or stolen',
        body='Report the lost or stolen device to IT/security immediately and provide the asset tag if known. Do not attempt to recover a stolen device yourself. IT/security can initiate account, device, and remote-management actions according to company policy.',
    ),
    dict(
        id='KB-1051', category='Security',
        title='Suspected malware or unusual computer behavior',
        body='Stop opening suspicious files or installing unapproved software. Record the symptoms and contact IT/security for investigation. Do not disable security software or attempt to remove suspected malware with unapproved tools.',
    ),
    dict(
        id='KB-1052', category='Security',
        title='Suspected account compromise',
        body='Report the incident to IT/security immediately and change the password through the approved process if company policy directs you to do so. Review recent sign-in activity if available and do not approve unexpected MFA requests. Security may need to revoke sessions or reset MFA.',
    ),
    dict(
        id='KB-1053', category='Security',
        title='Suspicious USB device found',
        body='Do not plug an unknown USB device into a company computer. Leave it isolated and report it to IT/security or the designated security team. Provide the location and any identifying label without opening files on the device.',
    ),
]

def seed_kb(db: Session):
    """Insert missing KB articles without duplicating existing rows."""
    existing_ids = {row.id for row in db.query(KBArticle.id).all()}
    added = 0
    for article in SEED_ARTICLES:
        if article["id"] not in existing_ids:
            db.add(KBArticle(**article))
            added += 1
    if added:
        db.commit()
