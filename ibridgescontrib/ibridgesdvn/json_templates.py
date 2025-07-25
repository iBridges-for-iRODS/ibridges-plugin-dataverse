"""Metadata templates for Dataverse."""

DATASET_JSON = """
{
  "datasetVersion": {
    "metadataBlocks": {
      "citation": {
        "fields": [
          {
            "value": "Youth in Austria 2005",
            "typeClass": "primitive",
            "multiple": false,
            "typeName": "title"
          },
          {
            "value": [
              {
                "authorName": {
                  "value": "LastAuthor1, FirstAuthor1",
                  "typeClass": "primitive",
                  "multiple": false,
                  "typeName": "authorName"
                },
                "authorAffiliation": {
                  "value": "AuthorAffiliation1",
                  "typeClass": "primitive",
                  "multiple": false,
                  "typeName": "authorAffiliation"
                }
              }
            ],
            "typeClass": "compound",
            "multiple": true,
            "typeName": "author"
          },
          {
            "value": [
              {
                "datasetContactEmail": {
                  "typeClass": "primitive",
                  "multiple": false,
                  "typeName": "datasetContactEmail",
                  "value": "ContactEmail1@mailinator.com"
                },
                "datasetContactName": {
                  "typeClass": "primitive",
                  "multiple": false,
                  "typeName": "datasetContactName",
                  "value": "LastContact1, FirstContact1"
                }
              }
            ],
            "typeClass": "compound",
            "multiple": true,
            "typeName": "datasetContact"
          },
          {
            "value": [
              {
                "dsDescriptionValue": {
                  "value": "DescriptionText",
                  "multiple": false,
                  "typeClass": "primitive",
                  "typeName": "dsDescriptionValue"
                }
              }
            ],
            "typeClass": "compound",
            "multiple": true,
            "typeName": "dsDescription"
          },
          {
            "value": [
              "Medicine, Health and Life Sciences"
            ],
            "typeClass": "controlledVocabulary",
            "multiple": true,
            "typeName": "subject"
          }
        ],
        "displayName": "Citation Metadata"
      }
    }
  }
}
"""
