
/*
 * Table to hold the unique statements
 */
create table if not exists postgres.daan_822.data_available_statement as
with data_statements as (
	select
		pmid,
		json_array_elements_text(data_available_details)  as statement
	from postgres.daan_822.article_detailed
	where data_available
)
select
	statement,
	count(*) as c
from data_statements
group by statement;

/*
 * View that creates our cleaned data
 * 
 */
create or replace view postgres.daan_822.v_article as
select 
	pmid,
	doi,
	article_type,
	article_title,
	article_subject,
	authors,
	pub_date,
	keywords,
	reference_count,
	license_type,
	journal_title,
	publisher_name,
	copyright_statement,
	copyright_year,
	abstract,
	affiliations,
	has_supplemental,
	figure_count,
	table_count,
	funding,
	data_available_details,
	data_available,
	code_available_details,
	code_available
from postgres.daan_822.article_detailed;


SELECT
    column_name,
    data_type,
    --is_nullable,
    --column_default,
    --character_maximum_length,
    --numeric_precision,
    numeric_scale
FROM information_schema.columns
WHERE table_schema = 'daan_822'
  AND table_name = 'article_detailed'
ORDER BY ordinal_position;


with funder as (
	select
		pmid,
		array_agg(doi) as dois
	from postgres.daan_822.funder
	group by pmid
),
"grant" as (
	select
		pmid,
		array_agg(nih_grant) as nih_grants,
		true as has_nih_grant
	from postgres.daan_822."grant"
	group by pmid
)
select 
	nullif(lower(trim(article_detailed.pmid)), '') as pmid,
	nullif(lower(trim(doi)), '') as doi,
	nullif(lower(trim(article_type)), '') as article_type,
	nullif(lower(trim(article_title)), '') as article_title,
	nullif(lower(trim(article_subject)), '') as article_subject,
	authors as authors,
	article_pub_date.pub_dt as pub_date,
	keywords as keywords,
	reference_count as reference_count,
	--license_type as license_type, -- remove all blank
	nullif(lower(trim(journal_title)), '') as journal_title,
	nullif(lower(trim(publisher_name)), '') as publisher_name,
	nullif(lower(trim(copyright_statement)), '') as copyright_statement,
	cast(nullif(lower(trim(copyright_year)), '') as int) as copyright_year,
	nullif(lower(trim(abstract)), '') as abstract,
	affiliations as affiliations,
	has_supplemental as has_supplemental,
	cast(nullif(lower(trim(figure_count)), '') as int) as figure_count,
	cast(nullif(lower(trim(table_count)), '') as int) as table_count,
	--funding as funding,
	funder.dois,
	"grant".has_nih_grant,
	data_available_details as data_available_details,
	data_available as data_available,
	code_available_details as code_available_details,
	code_available
from postgres.daan_822.article_detailed
left join postgres.daan_822.article_pub_date
	on
	article_detailed.pmid = article_pub_date.pmid
left join funder
	on
	article_detailed.pmid = funder.pmid
left join "grant"
	on
	article_detailed.pmid = "grant".pmid
	;


select count(*) from  postgres.daan_822.article_detailed; -- 7178


create table if not exists postgres.daan_822.article_pub_date as
select
	pmid,
	left(pub_date, 4) as pub_year,
	coalesce(trim(leading '0' from (regexp_match(pub_date, '[0-9]{4}-([0-9]{1,2})'))[1]), '1') as pub_month,
	coalesce(trim(leading '0' from (regexp_match(pub_date, '[0-9]{4}-[0-9]{1,2}-([0-9]{1,2})'))[1]), '1') as pub_day,
	cast('2027-01-01' as date) as pub_dt
from postgres.daan_822.article_detailed;


/*
 * Cast the strings to date type
update postgres.daan_822.article_pub_date
set pub_dt = cast(pub_year || '-' || pub_month || '-' || pub_day as date);
*/

select max(pub_dt) as max_pub_dt
from postgres.daan_822.article_pub_date;

-- 1k repeated ids
select count(*) from (
	select count(distinct pmid) as p,
	orcid
	from postgres.daan_822.author
	group by orcid
	having count(distinct pmid) > 1
);


/*
 * Extracted a handful of grant codes.
 * Better than nothing.
 */
create table if not exists postgres.daan_822.grant as
with funds as (
	select
	pmid,
	jsonb_array_elements_text(funding::jsonb) as funding
	from postgres.daan_822.article_detailed
	where jsonb_array_length(funding::jsonb) > 0
),
nih as (
	select 
	pmid,
    regexp_replace(
        (regexp_matches(
            funding,
            E'(?<![A-Za-z0-9])((?:R|K|F|T|U|P)\\d{2}[ -]?[A-Z]{2}\\d{6})(?![A-Za-z0-9])',
            'g'
        ))[1],
        '[ -]',
        '',
        'g'
    ) AS nih_grant,
	funding
	from funds
)
select *
from nih;


create table if not exists postgres.daan_822.funder as
WITH funds AS (
    SELECT
        pmid,
        jsonb_array_elements_text(funding::jsonb) AS funding
    FROM postgres.daan_822.article_detailed
    WHERE jsonb_array_length(funding::jsonb) > 0
),
dois AS (
    SELECT
        pmid,
        (regexp_matches(
            funding,
            E'(10\.[0-9]{4,9}\/[^[:space:]A-Z]+)',
            'g'
        ))[1] AS doi,
        funding
    FROM funds
    WHERE funding ~
        E'10\\.\\d{4,9}/[^\\s"\'<>\\]]+'
)
SELECT *
FROM dois;

select count(distinct pmid) from postgres.daan_822.funder; -- 1578