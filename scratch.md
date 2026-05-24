** NEW VERSION **
- Intro
    - Who we are
    - Why ER
- Operationalising, what does it mean ?
- Best ER is the one you don't need
    - Show raw data
    - Explain importance of dq techniques
        - normalization, enrichment with dicts, suffix/prefix expansion etc...
    - Show after
    - be inspired from the data in take2/assets/data/companies_raw/normalised
- Operational architecture
    - components:
        - data
        - Hume/Neo4j
        - Senzing
    - Full architecture we will follow
        - blocks we're now here
        - etc
- Phase 1
    - Data in, cleaned ( cleaning doesn't have to be in Hume )
    - Data in the graph is "exploded" ( graph format )
    - Data is disconnected


- Phase 2

- Attribute based ER
    - Deep explanation from Paco about Senzing, how it works etc..
    - What is good data for Senzing ?
    - Concepts : record, entity, entity group ( graph )
    - Typical input output with Sz only

    - From graph records to Senzing
    - Show CDC or trigger based push to Sz
    - Show mapping
    - Show affected entities handling
    - Show representation of EG + records linking in graph

- What is OOTB is Senzing ?
    - geocoding
    - globalisation

- Phase 3 

- A living architecture
    - idempotence
    - Show what happens when records are updated/deleted
    - Show example where 
        - growth
        - merge
        - split
    - Redo mechanism


- Phase 4 
    - Explainability
    - Observability
    - Hypothetical Idea for a audit/history of ER changes architecture


- Phase 5

    - Decision layer in the graph
        - Using graph heuristics ( aka graph fragments ) is not possible from Senzing to "enhance resolution"
        - But, we can use those as a graph decision layer for ER
        - For eg, Sz doesn't say that two records are resolved togehter, but
            - We have face fingerprints as vectors in the graph with a high similarity
            - Sz resolve two businesses, but While business name and address for those 2 records are the same, the source data tells you there is a "OWNS" relationship between them ( they CAN'T be the same )
            - Same for Person, two are resolved but the source data tells us there is a FATHER relationship between two records, they CAN'T be the same
            - Other graph evidence would show a human immediately that they or can't be the same
        - How this works ? 
            - Force apart/merge with trust ids
            - Generated TRUST_ID set on records in the graph ( either same id or different id)
            - Trigger record upates
            - Fed to Sz
            - Affected entiteis
            - Result stored in graph
        - ER reinforcement loop

- Phase 6

    - COnsumption
        - See note after about Hume 3.0 feature
        - demo ofc
        - future improvements for ER Graphs
            - Smart ER search
            - Better grouping visuals
            - ...



**Smart ER in Advanced Expand**

Effortlessly navigate entity-resolved graphs
When data from multiple systems is combined, the same real-world entity often appears more than once. A person, organisation, or location may exist in several datasets, each represented by a separate node in the graph.

Rather than merging those records into a single node and losing important context, GraphAware Hume uses entity groups to connect records that likely represent the same real-world entity while preserving their source data. This allows analysts to understand relationships across sources while still maintaining provenance, data separation, and access control.


In previous versions of GraphAware Hume, analysts needed to be aware of these entity groups when building queries or performing advanced expands, adding an extra layer of complexity to investigative workflows.

In GraphAware Hume 3.0, that complexity has been removed.

Analysts can query and explore their data as if they were working with a single entity, without needing to manage the underlying entity resolution logic.

The result is a simpler, more intuitive analytical experience while still preserving the flexibility, security, and data transparency required for graph-powered intelligence analysis. 


---

**PREVIOUS VERSION BELOW**
Operationalising Entity Resolved Graphs

Dataset

Cleaning and aligning always better
What is good data for ER
How ER starts with data quality analysis
How we work and produce a transparent overlay that generates some graph elements
Globalisation ( arabic, english, how do you merge these across languages and cultures )
Geocoding for addresses ( if you use some street names from caribbean but geocoding goes to india, then probably its India so you need to calibrate for errors )
Simple flow architecture ( graphs to senzing )
Push records to senzing
Senzing magic
Output -> affected entities
Idempotence -> any order we get the same results
Storing resolved entities in the graph
Source level security constraints
EntityGroup concept
The problems this model introduces as well
Co-occurrence/Community on top of co-occurrences graph -> analyse communities
Updates -> Going  in/out of entity when data changes, show this near real time
Redo logic -> what is it, features that are leading to more redo than others
Using graph heuristics as additional decision layer for resolution
FORCE MERGE and FORCE APART based on graph information
Show couple of real world examples
It goes back again in same process
Consuming ER graphs
Show new feature of hume 3
Lessons learned



—

TODO : Paco to send that OO/OS subset
	Here’s a GitHub repo with the OO/OS subset https://github.com/DerwenAI/min_aml




