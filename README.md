#OpenStreetMap

###Data Details
#####Location: Somersville, Massachusetts, United States of America
#####Downloaded: March 23, 2015
#####Size: 133.4 MB

###Process Blueprint
0. Identify target data
1. Audit data
2. Develop plan for cleaning
3. Write code to clean data
4. Execute code

###Step 0: Review Data & Identify Focus Areas
####Answer:
  * Where should I focus my attention?
  * What data should I target for cleaning?

####Focus:
  * Identify most frequently occuring attributes

####Tools: OsmDescribe

####OsmDescribe Documentation
#####Method: describe_elements()

Pretty prints a Python dictionary; keys = type of element, values = frequency of key

Returns None


#####Method: describe_element_attributes(element_name)
Allow you to explore the types of data contained within a certain element.

Pretty prints a Python dictionary; keys = type of element, values = frequency of key

Returns None


#####Method: describe_element_attribute_values(element_name, attribute_name)
Allow you to explore the values associated with a particular attribute of a particular element

Pretty prints a Python dictionary; keys = attribute value, values = frequency of attribute value

Returns None


#####Method: describe_elem_attr_vals_tree()
Similar to describe_element_attribute_values BUT this method breaks apart compound attributes delimited by a colon.
This method is most useful for grouping the "k" attribute of the "tag" element.

Write JSON object to report_data directory/; key = name of attribute, value = object representing parsed attribute value

Returns Python dictionary; key = name of attribute, value = object representing parsed attribute value



#####Method: describe_top_attr_vals()
Returns top 10 most frequently occuring attribute values.
This method is most useful for identifying most frequeny "k" attributes values of the "tag" element.




##Step 1: Audit Data
###Answer:
  * Is my data consistent?
  
###Focus:
  * Identify most common errors with those attributes