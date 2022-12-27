# AGSO Knokke-Heist watermeter integration for Home Assistant

The muncipality Knokke-Heist at the coast of Belgium has it's own drinking water
company which is called AGSO (Autonome Gemeentelijk StadsOntwikkelingsbedrijf),
which losely translates to 'Autonomous city development company'. Recently they
started rolling out smart water meters. In my home it is the
'Kamstrup MULTICAL® 21' meter wich is Sigfox connected.

According to the documentation these meters support an addon for a reed relay
to have live measurements based on a fixed amount of water which passed the
meter for every received pulse. This integration however logs in to the AGSO
cloud to get the official readings. This is required because you cannot get an
absolute meter value through the pulse connection which would require you to
calibrate your counter in case someone is using water when the pulse counter
resets or reboots.