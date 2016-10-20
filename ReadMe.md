# TriMet Tracker
*Making commutes a hair less painful each and every day you must drive.*
<hr>

#### **Requirements**
  1. Registered AppId from TriMet
  1. GoogleMapsAPI api_key from GoogleDevelopers
  1. Store these keys within a file in your environment: $HOME/.API_KEYS, with expected vars:
  
  *(Use these vars with Bash syntax)*
    - GOOGLEMAP_API_KEY=blah   
    - TRIMET_APPID=blah

#### **Launch**

  - ```python find_southery_buses_trimet.py [-d] [-lat] [-lon]```
    
#### **Options:**
- \-d (distance, in miles, from your location) 
- \-lat (degrees)
- \-lon (degrees)

*A suitable set of values will be selected by default*

<hr>     
### v1.0.0
    - Now using argparse
