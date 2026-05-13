
### **1\. Core User & Account Tables**

These tables handle authentication and the base identity of anyone on the platform.

**Users**

* user\_id (PK, UUID)  
* email (String, Unique)  
* password\_hash (String)  
* role (Enum: 'BRAND', 'AGENCY', 'DIRECTOR', 'KOL', 'ADMIN')  
* created\_at (Timestamp)  
* last\_login (Timestamp)  
* status (Enum: 'ACTIVE', 'PENDING', 'SUSPENDED')

**CompanyProfiles** (For Brands and Agencies)

* company\_id (PK, UUID)  
* user\_id (FK \-\> Users)  
* company\_name (String)  
* industry (String)  
* website (String)  
* contact\_name (String)  
* contact\_phone (String)

### ---

**2\. Talent Profiles (Directors & KOLs)**

Directors and KOLs have very different data points. Directors are matched on portfolio and style, while KOLs are matched on audience metrics and platform reach.

**DirectorProfiles**

* director\_id (PK, UUID)  
* user\_id (FK \-\> Users)  
* full\_name (String)  
* bio (Text)  
* years\_of\_experience (Int)  
* base\_day\_rate (Decimal)  
* primary\_location (String)  
* availability\_status (Boolean)

**KOLProfiles**

* kol\_id (PK, UUID)  
* user\_id (FK \-\> Users)  
* stage\_name (String)  
* bio (Text)  
* main\_niche (String) — *e.g., Beauty, Tech, Lifestyle*  
* target\_demographic\_age (String) — *e.g., '18-24', '25-34'*  
* booking\_fee\_estimate (Decimal)

**KOL\_SocialMetrics** (Tracks live data for KOLs)

* metric\_id (PK, UUID)  
* kol\_id (FK \-\> KOLProfiles)  
* platform (Enum: 'TIKTOK', 'YOUTUBE', 'INSTAGRAM', 'FACEBOOK')  
* handle\_url (String)  
* follower\_count (Int)  
* avg\_engagement\_rate (Decimal)  
* last\_updated (Timestamp)

**Portfolios** (Crucial for Directors)

* portfolio\_id (PK, UUID)  
* user\_id (FK \-\> Users) — *Could apply to KOLs too*  
* project\_title (String)  
* video\_url (String) — *Link to Vimeo/YouTube*  
* role\_played (String) — *e.g., 'Main Director', 'DoP'*  
* thumbnail\_url (String)

### ---

**3\. Taxonomy & Categorization (For Matching)**

To make the matching algorithm work, you need structured tags.

**Categories** (e.g., TVC, Music Video, Documentaries, Tech Review, Fashion)

* category\_id (PK, UUID)  
* name (String)  
* type (Enum: 'GENRE', 'INDUSTRY', 'SKILL')

**UserCategories** (Many-to-Many mapping)

* user\_id (FK \-\> Users)  
* category\_id (FK \-\> Categories)

### ---

**4\. Project & Campaign Tables**

Where Brands/Agencies post their requirements.

**Projects**

* project\_id (PK, UUID)  
* company\_id (FK \-\> CompanyProfiles)  
* title (String)  
* description (Text)  
* project\_type (Enum: 'COMMERCIAL', 'MUSIC\_VIDEO', 'KOL\_CAMPAIGN', 'EVENT')  
* budget\_min (Decimal)  
* budget\_max (Decimal)  
* shooting\_location (String)  
* timeline\_start (Date)  
* timeline\_end (Date)  
* status (Enum: 'DRAFT', 'OPEN', 'IN\_PROGRESS', 'COMPLETED', 'CANCELLED')

**ProjectRequirements**

* requirement\_id (PK, UUID)  
* project\_id (FK \-\> Projects)  
* talent\_type (Enum: 'DIRECTOR', 'KOL')  
* required\_category\_id (FK \-\> Categories)  
* min\_followers (Int) — *Null for Directors*

### ---

**5\. The "Matching" Engine (Workflow)**

This maps directly to the tracking steps seen in your "Quy trình ALIEN.csv" (e.g., Pitching, Approval).

**Matches\_Applications**

* match\_id (PK, UUID)  
* project\_id (FK \-\> Projects)  
* talent\_user\_id (FK \-\> Users)  
* initiated\_by (Enum: 'TALENT\_APPLIED', 'BRAND\_INVITED', 'SYSTEM\_MATCH')  
* status (Enum: 'PENDING', 'SHORTLISTED', 'PITCHING', 'REJECTED', 'HIRED')  
* proposed\_fee (Decimal)  
* match\_score (Decimal) — *If using an AI/Algorithm to score fit*  
* created\_at (Timestamp)

### ---

**6\. Post-Project Data (Feedback Loop)**

To improve future matching, you need to collect data after the project finishes.

**Reviews**

* review\_id (PK, UUID)  
* project\_id (FK \-\> Projects)  
* reviewer\_id (FK \-\> Users) — *The Brand/Agency*  
* reviewee\_id (FK \-\> Users) — *The Talent*  
* rating (Int) — *1 to 5 scale*  
* feedback (Text)  
* punctuality\_score (Int)  
* creativity\_score (Int)

### **System Flow Example (Tying it to your Workflow Data):**

1. **Pitching Stage:** An Agency creates a Project. The system queries the KOLProfiles, DirectorProfiles, and Categories to generate a list of candidates.  
2. **Shortlisting:** Selected candidates are added to the Matches\_Applications table with the status SHORTLISTED.  
3. **Pre-Production:** Once the Client approves the Director/KOL, the match status changes to HIRED, and the real-world production workflow (as detailed in your ALIEN process files) kicks off.