```
curl -XPUT 'http://elasticsearch2.trunk.koolearn.com/class_product_auth_20181220?pretty' -d '{
  "settings": {
    "index": {
      "number_of_replicas": "1",
      "number_of_shards": "10"
    }
  },
  "mappings": {
    "tb_product": {
      "properties": {
        "activity_days": {
          "type": "integer"
        },
        "apply_agent": {
          "type": "integer"
        },
        "bill_type": {
          "type": "integer"
        },
        "create_time": {
          "type": "date",
          "store": true,
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "create_uid": {
          "type": "string",
          "index": "not_analyzed"
        },
        "create_username": {
          "type": "string",
          "index": "not_analyzed"
        },
        "current_price": {
          "type": "string",
          "index": "not_analyzed"
        },
        "description": {
          "type": "string"
        },
        "display_name": {
          "type": "string"
        },
        "display_product_info": {
          "type": "integer"
        },
        "exam_season_id": {
          "type": "integer"
        },
        "expiration_date": {
          "type": "date",
          "store": true,
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "extension_type": {
          "type": "integer"
        },
        "first_online_time": {
          "type": "date",
          "store": true,
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "last_offline_time": {
          "type": "date",
          "store": true,
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "id": {
          "type": "integer"
        },
        "initial_sales_count": {
          "type": "integer"
        },
        "is_deleted": {
          "type": "integer"
        },
        "launch_date": {
          "type": "date",
          "store": true,
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "name": {
          "type": "string"
        },
        "original_price": {
          "type": "string",
          "index": "not_analyzed"
        },
        "picture_url": {
          "type": "string",
          "index": "not_analyzed"
        },
        "pre_sales_name": {
          "type": "string"
        },
        "product_line": {
          "type": "integer"
        },
        "product_type": {
          "type": "integer"
        },
        "protocol_id": {
          "type": "integer"
        },
        "remark": {
          "type": "string"
        },
        "sales_count": {
          "type": "long"
        },
        "status": {
          "type": "integer"
        },
        "supplement_service": {
          "type": "integer"
        },
        "template_product_id": {
          "type": "integer"
        },
        "to_search": {
          "type": "integer"
        },
        "ts": {
          "type": "date",
          "store": true,
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "update_time": {
          "type": "date",
          "store": true,
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "update_uid": {
          "type": "string",
          "index": "not_analyzed"
        },
        "update_username": {
          "type": "string",
          "index": "not_analyzed"
        },
        "view_type": {
          "type": "integer"
        },
        "wforder_id": {
          "type": "integer"
        }
      }
    },
    "pe_product_extended_attribute": {
      "_parent": {
        "type": "tb_product"
      },
      "_routing": {
        "required": true
      },
      "properties": {
        "id": {
          "type": "integer"
        },
        "is_deleted": {
          "type": "integer"
        },
        "product_id": {
          "type": "integer"
        },
        "ts": {
          "type": "date",
          "store": true,
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "type": {
          "type": "integer"
        },
        "value": {
          "type": "string",
          "index": "not_analyzed"
        }
      }
    }
  }
}'

```