### Basic Request Settings
POST
`http://<DEVICE_IP>:49153/upnp/control/deviceevent1`

### Headers
- Content-Type → text/xml; charset="utf-8"
- SOAPACTION → "urn:Belkin:service:deviceevent:1#SetAttributes"

### Body
```xml
<?xml version="1.0"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
  <s:Body>
    <u:SetAttributes xmlns:u="urn:Belkin:service:deviceevent:1">
      <attributeList>&lt;attribute&gt;&lt;name&gt;Mode&lt;/name&gt;&lt;value&gt;4&lt;/value&gt;&lt;/attribute&gt;</attributeList>
    </u:SetAttributes>
  </s:Body>
</s:Envelope>
```
