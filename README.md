# Plugin - Intercom to S3/GCS

This plugin moves data from the [Intercom](https://developers.intercom.com/v2.0/docs) API to S3/GCS based on the specified object

## Hooks
### IntercomHook
This hook handles the authentication and request to Intercom. Based on [python-intercom](https://github.com/jkeyes/python-intercom) module.

## Operators
### IntercomToS3Operator
This operator composes the logic for this plugin. It fetches the intercom specified object and saves the result in a S3 Bucket, under a specified key, in
njson format. The parameters it can accept include the following.

- `intercom_conn_id`: The intercom connection id from Airflow
- `intercom_obj`: Intercom object to query
- `intercom_method`: *optional* Method from python-intercom.
- `s3_conn_id`: S3 connection id from Airflow.  
- `s3_bucket`: The output s3 bucket.  
- `s3_key`: The input s3 key.  
- `fields`: *optional* list of fields that you want to get from the object. If *None*, then this will get all fields for the object
- `replication_key`: *optional* name of the replication key, if needed.
- `replication_key_value`: *(optional)* value of the replication key, if needed. The operator will import only results with the property from replication_key grater than the value of this param.
- `intercom_method`: *(optional)* method to call from python-intercom. Default to "all".
- `**kwargs`:  replication key and value, if replication_key parameter is given and extra params for intercom method if needed.

### IntercomToGCSOperator
This operator composes the logic for this plugin. It fetches the intercom specified object and saves the result in a GCS Bucket, under a specified key, in
njson format. The parameters it can accept include the following.

- `intercom_conn_id`: The intercom connection id from Airflow
- `intercom_obj`: Intercom object to query
- `intercom_method`: *optional* Method from python-intercom.
- `s3_conn_id`: GCS connection id from Airflow.  
- `s3_bucket`: The output sgcsbucket.  
- `gcs_key`: The input gcs object.  
- `fields`: *optional* list of fields that you want to get from the object. If *None*, then this will get all fields for the object
- `replication_key`: *optional* name of the replication key, if needed.
- `replication_key_value`: *(optional)* value of the replication key, if needed. The operator will import only results with the property from replication_key grater than the value of this param.
- `intercom_method`: *(optional)* method to call from python-intercom. Default to "all".
- `**kwargs`:  replication key and value, if replication_key parameter is given and extra params for intercom method if needed.
