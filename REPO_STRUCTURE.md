# BioNetGen Repository Structure Analysis for JS Visualization

## Overview

BioNetGen is software for the specification and simulation of rule-based models of biochemical systems, including signal transduction, metabolic, and genetic regulatory networks. This document provides a comprehensive analysis of the repository structure with emphasis on creating JavaScript-based visualizations.

## Technology Stack

- **Perl**: Core network generation engine
- **C++**: Network simulator (Network3)
- **Python**: SBML-to-BNGL translator and visualization tools
- **Java/ANTLR**: New language parser
- **JavaScript/D3.js**: Existing bipartite graph visualization

## Repository Structure

### Core Directories

#### `/bng2/` - Core BioNetGen Implementation
- `BNG2.pl` - Main entry point for BioNetGen
- `Perl2/` - Perl modules for model parsing and processing
  - `SpeciesGraph.pm` - Core species representation
  - `Molecule.pm` - Molecule structure and operations
  - `Component.pm` - Component (site) definitions
  - `RxnRule.pm` - Reaction rule implementation
  - `Species.pm` - Species management
  - `XMLReader.pm` - XML format reader
  - `Visualization.pm` - Visualization module for GML generation
- `Network3/` - C++ network simulator
- `Models2/` - Example models in BNGL format
- `Validate/` - Test models and validation data

#### `/parsers/` - Parsers and Visualization Tools
- `BNGParser/` - Java-based ANTLR parser
  - Generates XML/JSON output from BNGL
- `BipartiteGraph/` - Python bipartite graph visualization
  - `modelviz/` - **Existing D3.js web visualization**
    - Uses JSON data format with nodes and edges
    - Interactive rule and pattern visualization
- `ContactMap/` - Python contact map visualization
  - Shows potential binding interactions
  - Uses networkx for graph generation
- `utils/` - Python utilities
  - `readBNGXML.py` - BNG XML format reader
  - `smallStructures.py` - Python data structures

#### `/bng-graph/` - Graph Analysis Tools
- `nauty/` - Graph isomorphism library
- `BNGcore/` - C++ core functionality for graph operations

## Model File Format (BNGL)

BNGL (BioNetGen Language) files are structured as follows:

```bngl
begin model
  begin parameters
    # Rate constants and initial concentrations
    kf  0.1  # forward rate
    kr  0.01 # reverse rate
  end parameters
  
  begin molecule types
    # Declaration of molecules and their components
    Receptor(lig,Y~U~P)  # Receptor with ligand site and Y that can be U or P
    Ligand(rec)          # Ligand with receptor binding site
  end molecule types
  
  begin species
    # Initial molecular species
    Receptor(lig,Y~U)  1000
    Ligand(rec)        100
  end species
  
  begin reaction rules
    # Rules that generate reactions
    # Binding rule
    Receptor(lig) + Ligand(rec) <-> Receptor(lig!1).Ligand(rec!1)  kf, kr
    # Phosphorylation rule
    Receptor(lig!+,Y~U) -> Receptor(lig!+,Y~P)  kphos
  end reaction rules
  
  begin observables
    # Quantities to track during simulation
    Molecules  BoundReceptor  Receptor(lig!+)
    Molecules  PhosReceptor   Receptor(Y~P)
  end observables
end model

# Actions
generate_network({overwrite=>1})
simulate({method=>"ode",t_end=>100,n_steps=>50})
```

## Core Data Structures

### 1. SpeciesGraph
Central structure representing molecular complexes:
```perl
struct SpeciesGraph => {
    Name        => '$',           # Species name
    Label       => '$',           # Local label
    Compartment => 'Compartment', # Spatial compartment
    Molecules   => '@',           # Array of Molecule objects
    Edges       => '@',           # Bond definitions (2D array)
    Adjacency   => '%',           # Adjacency relationships
    StringID    => '$',           # Canonical label for isomorphism
    StringExact => '$',           # Exact canonical representation
    Quantifier  => '$',           # Pattern quantifier
    Species     => 'Species',     # Bound Species object
    MatchOnce   => '$',           # Single mapping constraint
    Fixed       => '$',           # Constant concentration flag
    IsCanonical => '$',           # Canonical form flag
    Automorphisms => '$'          # Graph automorphisms
};
```

### 2. Molecule
Represents individual molecules within species:
```perl
struct Molecule => {
    Name        => '$',        # Molecule type (e.g., "EGFR")
    State       => '$',        # Molecule-level state
    Edges       => '@',        # Bond labels
    Label       => '$',        # User label
    Compartment => 'Compartment',
    Components  => '@',        # Array of Component objects
    Context     => '$'         # Context-sensitive matching
};
```

### 3. Component
Represents molecular sites/components:
```perl
struct Component => {
    Name  => '$',              # Component name (e.g., "Y1068")
    State => '$',              # State (e.g., "U", "P")
    Edges => '@',              # Bonds or wildcards
    Label => '$',              # User label
    Compartment => 'Compartment'
};
```

### 4. RxnRule
Defines transformation rules:
```perl
struct RxnRule => {
    Name      => '$',
    Reactants => '@',          # SpeciesGraph patterns
    Products  => '@',          # SpeciesGraph patterns
    MapF      => '%',          # Forward mapping
    MapR      => '%',          # Reverse mapping
    RateLaw   => 'RateLaw',
    
    # Transformation operations
    EdgeAdd           => '@',  # Bonds to add
    EdgeDel           => '@',  # Bonds to delete
    MolAdd            => '@',  # Molecules to add
    MolDel            => '@',  # Molecules to delete
    CompStateChange   => '@',  # State changes
    ChangeCompartment => '@'   # Compartment changes
};
```

## Key Concepts for Visualization

### 1. Molecular Representation
- **Molecules**: Main entities (circles/shapes)
- **Components**: Sites on molecules (smaller shapes on periphery)
- **States**: Component properties (colors/labels)
- **Bonds**: Connections between components (lines with labels !1, !2, etc.)

### 2. Pattern Notation
- `A(x)` - Molecule A with component x unbound
- `A(x!1).B(y!1)` - A bound to B through components x and y
- `A(x~P)` - Component x in state P (phosphorylated)
- `A(x!+)` - Component x with one or more bonds
- `A(x!?)` - Component x with zero or one bond

### 3. Rule Transformations
- **Bond formation**: `A(x) + B(y) -> A(x!1).B(y!1)`
- **Bond breaking**: `A(x!1).B(y!1) -> A(x) + B(y)`
- **State change**: `A(x~U) -> A(x~P)`
- **Molecule creation**: `0 -> A()`
- **Molecule deletion**: `A() -> 0`

## Output Formats

### 1. Network File (.net)
Contains fully expanded reaction network:
```
begin species
    1 A(x~U,y)  1000
    2 B(a,b~P)  500
    3 A(x~U,y!1).B(a!1,b~P)  0
end species

begin reactions
    1 1,2 3 kf
    2 3 1,2 kr
end reactions
```

### 2. Observable Data (.gdat)
Time series data for tracked observables:
```
# time    Observable1    Observable2
0.0       1000          500
1.0       950           450
2.0       910           420
```

### 3. XML Format
Structured representation of model elements with full annotations.

### 4. GML Format
Graph Modeling Language for visualization tools:
```gml
graph [
  directed 1
  node [
    id 0
    label "A(x~U)"
    graphics [ type "roundrectangle" fill "#FFE9C7" ]
  ]
  edge [
    source 0
    target 1
    graphics [ style "dashed" ]
  ]
]
```

### 5. JSON Format (Bipartite Visualization)
Used by existing D3.js visualization:
```json
{
  "nodes": [
    {"type": "r", "name": "Rule1", "idx": 0},
    {"type": "p", "name": "A(x)", "idx": 1},
    {"type": "t", "name": "Binding", "idx": 2}
  ],
  "edges": {
    "r2t": [[0, 2]],
    "t2p": {
      "reactant": [[2, 1]],
      "product": [[2, 3]]
    }
  }
}
```

## Network Generation Process

1. **Pattern Matching**: Rules search for matching patterns in existing species
2. **Map Generation**: Creates mappings between pattern and species elements
3. **Transformation**: Applies rule operations (add/delete bonds, change states)
4. **Species Creation**: Generates new species if transformation creates novel configuration
5. **Canonical Labeling**: Uses HNauty algorithm for graph isomorphism detection
6. **Reaction Instance**: Creates specific reaction with calculated rates

## Visualization Requirements

### 1. Core Visualizations Needed

#### a. Molecular Complex View
- Interactive force-directed layout for molecules and bonds
- Component states shown as colors/shapes
- Bond labels and constraints
- Zoom/pan for large complexes

#### b. Reaction Network
- Species as nodes
- Reactions as directed edges
- Flow visualization (Sankey diagram option)
- Concentration dynamics overlay

#### c. Rule Pattern View
- Before/after pattern visualization
- Highlight transformation operations
- Show all possible matches in current species pool

#### d. Contact Map
- Matrix view of potential binding interactions
- Based on complementary binding sites
- Useful for large models

#### e. Time Series Plots
- Observable dynamics from .gdat files
- Multi-scale time support
- Parameter sensitivity analysis

### 2. Interactive Features
- Click species to see constituent molecules
- Click rules to see affected species
- Pattern search and highlighting
- Animation of rule application
- Export to various formats (SVG, PNG, JSON)

## Implementation Recommendations

### 1. Architecture
```
BNG Model → Parser → JSON → D3.js Visualization
    ↓                           ↑
   .net/.xml files          WebSocket for
                            live updates
```

### 2. Parser Options
- Use existing BNGParser (Java) to generate JSON
- Create lightweight JS parser for BNGL subset
- Use Python scripts to convert .net → JSON
- WebAssembly module from C++ parser

### 3. Visualization Libraries
- **D3.js**: Primary visualization library
- **Force Layout**: Molecular complexes
- **Sankey**: Reaction flows
- **Cytoscape.js**: Alternative for large networks
- **Plot.ly**: Time series visualization

### 4. Data Management
- IndexedDB for large models
- Web Workers for network generation
- Virtual scrolling for species lists
- LOD (Level of Detail) for large networks

### 5. Key Features to Implement
1. BNGL syntax highlighting editor
2. Real-time pattern matching visualization
3. Rule debugger showing step-by-step application
4. Comparative visualization (multiple models)
5. 3D molecular complex visualization (Three.js)

## Existing Resources to Leverage

1. **Bipartite Graph Viz** (`/parsers/BipartiteGraph/modelviz/`)
   - Already has D3.js integration
   - Node and edge data structures
   - Can be extended for full model visualization

2. **XML Reader** (`/parsers/utils/readBNGXML.py`)
   - Parses BNG XML format
   - Can be ported to JavaScript

3. **GML Generation** (`/bng2/Perl2/Visualization.pm`)
   - Graph layout algorithms
   - Can inform JS implementation

4. **Example Models** (`/bng2/Models2/`)
   - Test cases for visualization
   - Range from simple to complex

## Next Steps

1. **Create JSON Schema** for complete BNG model representation
2. **Build Parser** (BNGL → JSON) in JavaScript or use existing tools
3. **Develop Core Visualizations** starting with molecular complexes
4. **Implement Interactivity** for model exploration
5. **Add Analysis Tools** for model debugging and understanding
6. **Create Documentation** and tutorials for users

This analysis provides the foundation for building a comprehensive JavaScript-based visualization suite for BioNetGen models, enabling researchers to better understand and communicate complex biological systems.