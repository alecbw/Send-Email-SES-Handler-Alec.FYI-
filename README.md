# Using this


This repo uses the serverless.com Infrastructure-as-code platform (which itself wraps AWS CloudFormation).

To create a CloudFormation Stack (and also subsequently update it), use:
``` sls deploy ```

You can test the Lambda locally (be aware it does send an actual email) with:
```sls invoke local -f send-email -d '{"Recipients":["recipient@your-domain.com"], "Subject":"CLI Test", "Body":"testing 1 2 3"}'```
