import logging
import json
import collections
from airflow.contrib.hooks.gcs_hook import GoogleCloudStorageHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from intercom_plugin.hooks.intercom_hook import IntercomHook
from tempfile import NamedTemporaryFile


class IntercomToGCSOperator(BaseOperator):
    """
    Make a query against Intercom and write the resulting data to gcs.
    """
    template_field = ('gcs_object', )

    @apply_defaults
    def __init__(
            self,
            intercom_conn_id,
            intercom_obj,
            intercom_method='all',
            gcs_conn_id='',
            gcs_bucket='',
            gcs_object='',
            fields=None,
            replication_key_name=None,
            replication_key_value=0,
            *args,
            **kwargs
    ):
        """
        Initialize the operator
        :param intercom_conn_id:        name of the Airflow connection that has
                                        your Intercom tokens
        :param intercom_obj:            name of the Intercom object we are
                                        fetching data from
        :param gcs_conn_id:              name of the Airflow connection that has
                                        your GCS conection params
        :param gcs_bucket:               name of the destination GCS bucket
        :param gcs_object:                  name of the destination file from bucket
        :param fields:                  *(optional)* list of fields that you want
                                        to get from the object.
                                        If *None*, then this will get all fields
                                        for the object
        :param replication_key_name:     *(optional)* name of the replication key,
                                        if needed.
        :param replication_key_value:   *(optional)* value of the replication key,
                                        if needed. The operator will import only
                                        results with the property from replication_key
                                        grater than the value of this param.
        :param intercom_method          *(optional)* method to call from python-intercom
                                        Default to "all".
        :param \**kwargs:               Extra params for the intercom query, based on python
                                        intercom module
        """

        super().__init__(*args, **kwargs)

        self.intercom_conn_id = intercom_conn_id
        self.intercom_obj = intercom_obj
        self.intercom_method = intercom_method

        self.gcs_conn_id = gcs_conn_id
        self.gcs_bucket = gcs_bucket
        self.gcs_object = gcs_object

        self.fields = fields
        self.replication_key_name = replication_key_name
        self.replication_key_value = replication_key_value
        self._kwargs = kwargs

    def filter_fields(self, result):
        """
        Filter the fields from an resulting object.

        This will return a object only with fields given
        as parameter in the constructor.

        All fields are returned when "fields" param is None.
        """
        if not self.fields:
            return result
        obj = {}
        for field in self.fields:
            obj[field] = result[field]
        return obj

    def filter(self, results):
        """
        Filter the results.
        This will filter the results if there's a replication key given as param.
        """
        if not isinstance(results, collections.Iterable):
            return json.loads((json.dumps(results, default=lambda o: o.__dict__)))

        filtered = []
        for result in results:
            result_json = json.loads((json.dumps(result,
                                                 default=lambda o: o.__dict__)))

            if not self.replication_key_name or \
                    int(result_json[self.replication_key_name]) >= int(self.replication_key_value):
                filtered.append(self.filter_fields(result_json))
        logging.info(filtered)

        return filtered

    def execute(self, context):
        """
        Execute the operator.
        This will get all the data for a particular Intercom model
        and write it to a file.
        """
        logging.info("Prepping to gather data from Intercom")
        hook = IntercomHook(
            conn_id=self.intercom_conn_id,
        )

        # attempt to login to Intercom
        # if this process fails, it will raise an error and die right here
        # we could wrap it
        hook.get_conn()

        logging.info(
            "Making request for"
            " {0} object".format(self.intercom_obj)
        )

        # fetch the results from intercom and filter them

        results = hook.run_query(self.intercom_obj, self.intercom_method)
        filterd_results = self.filter(results)

        # write the results to a temporary file and save that file to gcs
        with NamedTemporaryFile("w") as tmp:
            for result in filterd_results:
                tmp.write(json.dumps(result) + '\n')

            tmp.flush()

            gcs_conn = GoogleCloudStorageHook(self.gcs_conn_id)
            gcs_conn.upload(self.gcs_bucket, self.gcs_object, tmp.name)

            tmp.close()

    logging.info("Query finished!")
