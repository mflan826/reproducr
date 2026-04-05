# Data Collection

## Bias in sample collected

5.1.1 Potential for Bias

The sample of articles we can collect will be inherently biased, because full participation in PubMed Central (PMC) full text article repository is voluntary. https://pmc.ncbi.nlm.nih.gov/pub/agreements/ Publishers are, however, required to share the text of articles with NIH funding. Our sample will potentially overrepresent NIH funded research compared to all articles published in the same time period. It's worth noting that NIH funded research is required to make their data publicly available, which could mean that we overrepresent data availability, specificaly.
Publishers that do not participate in PMC will be underrepresented. Any publisher with an incentive to not release the full text of their published articles for free is likely to be underrespresented in our sample. If there is a correlation between non-participating publishers and including or not including a data availability statement, we would underrepresent that correlation in our dataset, compared to all articles published in the given time period.

Taken together, we must be careful to specify that we draw our conclusions about the kinds of publishers, authors, and specialties that make their work available on PMC, within the chosen time period. We do not speak for all research published in the given time period, or research outside of our time period. But we expect to draw conclusions about the usefulness of the data which is available.

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