---
title: How to connect to your data in a postgresql database
---
import AddingCredentials from '../reference/database_credentials.md'
import NextSteps from '../reference/link-to-validator.md'
import ConnectionStringDetails from '../reference/configuration_explanation.md'
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

This guide will help you connect Great Expectations to data in a Postgresql database. We will be building a `Datasource` configuration, and using it to verify connectivity. By the end of this how-to guide, you should have a `Batch` representing a slice of data in your database, and a working code snippet that can be used as a starting point for more complex configurations.

:::note Prerequisites: This how-to-guide assumes you have already:
- Completed the [Getting Started Tutorial.](../../tutorials/quick-start.md)
- Have a working installation of Great Expectations.
- Have data on Postgresql database that you would like to connect to.
:::

## Steps

### 1. Determine how to add credentials to configuration

Great Expectations provides multiple methods of providing credentials for accessing databases. For our current example will use a `connection_string`, but other options include providing an Environment Variable, and loading from a Cloud Secret Store.  

For more information, please refer to [Additional Notes](#additional-notes).

```
postgresql+psycopg2://postgres:@localhost/test_ci
```

<details><summary><b>What's in the config?</b></summary>
<p>
<ConnectionStringDetails />
</p>
</details>

### 2. Install required packages

Next make sure you have the necessary packages for Great Expectations to connect to your postgres database.

```console
pip install sqlalchemy psycopg2
```

### 3. Load the DataContext into memory

<details><summary><b>More Details</b></summary>
<p>
Open up a Jupyter Notebook in the same directory as the `great_expectations/` folder. Import any necessary packages or modules.

```python file=../../../../integration/code/connecting_to_your_data/database/postgres.py#L1-L4
```

</p>
</details>

Load your DataContext into memory using the `get_context()` method.

```python file=../../../../integration/code/connecting_to_your_data/database/postgres.py#L13
```

### 4. Write your configuration as a YAML

Here is an example configuration:

```python file=../../../../integration/code/connecting_to_your_data/database/postgres.py#L19-L33
```

:::note What does the configuration contain?
A `Datasource` named `my_postgres_datasource`.

An `ExecutionEngine` with a `connection_string`.

The configuration also contains 2 `DataConnectors` by default:
1. A `RuntimeDataConnector` named `default_runtime_data_connector_name` which loads your data into a Batch, and a default `batch_identifier` which identifies your Batches.
2. A `InferredAssetSqlDataConnector` named `default_inferred_data_connector_name` which allows you to name a `whole_table` to retrieve your Batch.  
:::

:::warning
  - Add blurb about ActiveDataConnectors here
:::

:::warning
  - Add test for yaml here
:::

### 5. Save configuration to DataContext.

Save the configuration into your DataContext by running the `add_datasource()` function.

```python file=../../../../integration/code/connecting_to_your_data/database/postgres.py#L37
```

### 6. Test Configuration

Test your configuration by retrieving a Validator from Great Expectations using a `BatchRequest`.

<Tabs
  defaultValue='runtime_batch_request'
  values={[
  {label: 'Using a Query', value:'runtime_batch_request'},
  {label: 'Naming a Table', value:'batch_request'},
  ]}>
  <TabItem value="runtime_batch_request">

Here is an example of loading a batch from a query. As you can see in the following snippet, when we fetch a Batch of data, we actually create a Validator, which is a Batch + ExpectationSuite. This allows you to perform operations like `.head()` to see 
the first few rows of your table, as well as run Expectations directly. 

```python file=../../../../integration/code/connecting_to_your_data/database/postgres.py#L41-L51
```

:::note What does the RuntimeBatchRequest contain?
1. `datasource_name` and `data_connector_name` are directly from our `Datasource` configuration.
2. `query` is passed in as a `runtime_parameter`, and is used to select 10 rows from table `taxi_data`.

**Note** : Make `data_asset_name` and `batch_identifiers` default.
:::



  </TabItem>

  <TabItem value="batch_request">

Here is an example of loading a batch by naming a table. As you can see in the following snippet, when we fetch a Batch of data, we actually create a Validator, which is a Batch + ExpectationSuite. This allows you to perform operations like `.head()` to see 
the first few rows of your table, as well as run Expectations directly. 

```python file=../../../../integration/code/connecting_to_your_data/database/postgres.py#L54-L62
```

:::note What does the BatchRequest contain?
1. `datasource_name` and `data_connector_name` are directly from our `Datasource` configuration.
2.  `data_asset_name` is `taxi_data`, which is the name of the table we want to retrieve as a batch.  
The reason we can do this is because of the `InferredAssetDataConnector` that is configured to retrieve `whole_table` by default.

**To Discuss**: How much do we mention `ActiveDataConnector` here?
:::


  </TabItem>
</Tabs>

<NextSteps />

## Additional Notes

<AddingCredentials />