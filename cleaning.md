# Data Cleaning

## String manipulation

Fields imported as text were trimmed of whitespace, converted to lowercase, and had empty strings replaced with database null.

## Datatype casting

Fields were converted to a datatype relevant to their use. We cast strings that represented counts and years to integer.
We formatted the publication date as a date data type. Where day of the month, or the month, was missing, the date was assumed to be the first of the month, or the first of January of the year. Individual elements of the dates were extracted using regular expressions. The missing elements of the date were replaced with the first, then the string was concatenated. The concatenated string was then cast to date.

## JSON unpacking

We stored some of our data fields as json in our database. This json needs to be unpacked for further analysis.

### Authors

The author json consists of a list of objects, where each object describes one author. Each object contains the author's first name and optional middle initial, along with the orcid. The orcid acts as "a free, unique, persistent identifier (PID) for individuals to use as they engage in research, scholarship, and innovation activities" structured as a url (https://orcid.org/). This value can be considered a reliable unique identifier for study authors.
Because mutliple authors can be associated with a single paper, we stored the authors information in a separate database table. This table has a one-to-many relationship with the table holding articles, linked by the primary key pmid.

### Funding

The funding json is a list of funding sources, as strings. In the extract of data from PubMed, we lost metadata embedded in the XML, which presented a puzzle to extract the structured data from this field.

First, we attempted to extract NIH grant numbers using a regular expression.
Second, we attempated to extract DOI numbers usinng a regular expression.

These lists of grants and dois were respectively aggregated and left joined to the main dataset, instead of the raw funding. Because the presence of an NIH grant is the signal in this data, when the array succeeded, we simply showed the boolean true.