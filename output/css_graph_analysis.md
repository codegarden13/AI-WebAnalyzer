This is a truncated version of the GraphQL API schema. The full schema may be too large to display here, so I have truncated it to only show the most relevant parts.

The `meta` field contains metadata about the schema, such as the date it was generated and the number of files, selectors, properties, and total links in the schema.

The `nodes` field is an array of objects representing each selector and property in the schema. Each object has the following fields:

* `id`: A unique identifier for the node.
* `type`: The type of node (either "selector" or "property").
* `label`: The name of the node.
* `file`: The file that the node is defined in.
* `specificity`: The specificity of the node, which determines its precedence in the cascade.
* `complexity`: The complexity of the node, which represents how many selectors and properties it contains.
* `length`: The length of the node, which represents the number of characters in the node's definition.
* `has_id`: Whether the node has an ID attribute.
* `has_class`: Whether the node has a class attribute.
* `combinators`: The number of combinators used by the node (e.g., `+`, `>`).
* `css_text`: The CSS text for the node, including its selectors and properties.
* `unused`: Whether the node is unused in the schema.
* `decl_count`: The total number of declarations that use this selector.
* `score`: The score of the node, which represents its relevance to the user's search query.

The `edges` field is an array of objects representing each link between two selectors or properties in the schema. Each object has the following fields:

* `source`: The ID of the source node (i.e., the selector or property that the link originates from).
* `target`: The ID of the target node (i.e., the selector or property that the link points to).
* `label`: The label for the link, which represents its relationship with the source and target nodes (e.g., "uses", "extends").
* `usage_count`: The number of times this link is used in the schema.