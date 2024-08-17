# AmazonQBusiness-Permissions
Permissions needed by Q Business admins:

If a user has an admin role then they will be able to create Q Business resources as described above. That said, there will be situations where the person creating Q Business resources doesn’t have an admin role. Thus, we have to make sure this person has the right permissions following the least-privileged principle.

For Q Business admin role, there are 7 AWS managed policies attached to the blueprint role. There are several policies are added for future Q Business related operation ease (such as Bedrock, Cloudformation and Lambda): 
 

* AWSCloudFormationFullAccess (Allow CloudFormation to create Q Business in the future), 
* AWSLambda_FullAccess (This is to allow future Document Enrichment process for image and video)
* AmazonBedrockFullAccess (This is to provide LLM for future document enrichment workflow)
* CloudWatchLogsFullAccess(This is the CloudWatch logs to troubleshoot issues)
* SecretManagerReadWrite (This is to allow secret manager to store and retrieve credential for other connectors in the future)

Besides these managed policies, there is one custom policy attached to this QBusiness admin role. This policy is to 

* Necessary organization operation for IDC 

                    - organizations:DescribeOrganization
                    - organizations:ListAWSServiceAccessForOrganization
                    - organizations:ListDelegatedAdministrators
                    - resource-explorer-2:ListIndexes

* IAM: operations to assign service linked role and pre-created data source and web experience roles to Q Business applications

                    - iam:GetAccountSummary
                    - iam:GetServiceLastAccessedDetails
                    - iam:ListAccountAliases
                    - iam:ListPolicies
                    - iam:ListRoles
                    - iam:ListUsers
                    - iam:GetRole
                    - iam:GetPolicy
                    - iam:GetPolicyVersion
                    - iam:PassRole
                    - iam:ListAttachedRolePolicies
                    - iam:ListInstanceProfilesForRole
                    - iam:ListRolePolicies
                    - iam:GetUser
                    - iam:ListUserPolicies
                    - iam:ListUserTags
                    - iam:ListGroupsForUser

* Signin (console access)
* sso (IDC)
* sso-directory (IDC)
* identitystore (IDC)
* identitystore-auth (IDC)
* UserSubscription (IDC)
* Q Business (Q Business service)
* Q apps  (Q Business service)
* cloudtrail (DescribeListCreate activities to monitor)
* aws config describe (resource management) 
* notification (Q Business monitor and notification)
* kms (potential key management needs)
* fsx(file storage access needs)
* service catalog (service/application management needs)
* Ec2 describe* (for future EC2 on-prem instance)
* CloudShell to perform CLI (troubleshooting)
* relevant S3 operation (list, get, put for s3 object management)

Permissions needed by the Service:

Q Business resources (like applications and web experiences) need permissions to access data sources.

Q Business also need to perform calls to other AWS Services (like Cloudwatch) on your behalf.

When you create a Q Business application, you need to provide Q Business the permissions mentioned earlier, and when you use the Q Business Console, you will have the chance to create these permissions “on-the-fly”. You will have the chance to create/use  a Service-linked role (SRL) or Service Role (SR).

Service-linked role (SLR): A type of IAM role managed by Amazon Q. This role is linked to Q Business and includes all the permissions the service requires to call other services on your behalf. The service linked role for Q Business has a AWS managed policy for necessary AWS services to manage/monitor Q Business application. 

Service-linked roles are useful because you don’t have to manually add/create permissions. For reference, this is the policy that the SLR uses. 

Service role (SR): Unlike SLR, you are manually creating a role for Q Business to assume. This role must have permissions to access AWS resources it needs to create your application.


Roles and Policies

Service Role

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AmazonQApplicationPutMetricDataPermission",
            "Effect": "Allow",
            "Action": [
                "cloudwatch:PutMetricData"
            ],
            "Resource": "",
            "Condition": {
                "StringEquals": {
                    "cloudwatch:namespace": "AWS/QBusiness"
                }
            }
        },
        {
            "Sid": "AmazonQApplicationDescribeLogGroupsPermission",
            "Effect": "Allow",
            "Action": [
                "logs:DescribeLogGroups"
            ],
            "Resource": ""
        },
        {
            "Sid": "AmazonQApplicationCreateLogGroupPermission",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup"
            ],
            "Resource": [
                "arn:aws:logs:{region}:{account-id}:log-group:/aws/qbusiness/"
            ]
        },
        {
            "Sid": "AmazonQApplicationLogStreamPermission",
            "Effect": "Allow",
            "Action": [
                "logs:DescribeLogStreams",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:{region}:{account-id}:log-group:/aws/qbusiness/:log-stream:*"
            ]
        }
    ]
}

Policy for Q Business to Assume a Role



{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowsAmazonQToAssumeRoleForServicePrincipal",
      "Effect": "Allow",
      "Principal": {
        "Service": "qbusiness.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "{{source_account}}"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:qbusiness:{{region}}:{{source_account}}:application/{{application_id}}"
        }
      }
    }
  ]
}

Permissions needed by Data source connector:

For each Q Business application, there are two other roles that need to be created: Data source and Web experience. If you use the console, you can either create an IAM role when you connect your data source to Amazon Q Business or use an existing role. From security perspective, Q Business admin role does not have IAM:CreateRole permission attached, so it is recommended to create these two roles via Cloudformation before the Q Business application creation. 

Role for Data Source

The specific permissions required depend on the data source. At a minimum, your IAM role must include the following:

* Permission to access the BatchPutDocument and BatchDeleteDocument API operations in order to ingest documents.
* Permission to access the User Store APIs needed to ingest access control and identity information from documents.

In the attached example, besides the above two operations, access to S3 permission is also added to use an S3 data source. Other permissions are added to make the role more generalized for more advanced operation, such as credential retrieval, VPC connection. These permissions allow the data source connector to use secret manager to retrieve credentials, connect VPC and create ENI for network interface.  are: AllowsAmazonQToDecryptSecret, AllowsAmazonQToCreateAndDeleteENI, AllowsAmazonQToCreateNetworkInterfacePermission, AllowsAmazonQToCreateTags. 

Role for Web Experience

For Web experience role, you can create basic role to decrypt data, and allow conversation and context permission. 

QBusinessKMSDecryptPermissions
QBusinessConversationPermission
QBusinessSetContextPermissions


If the users of your deployed web experience want to create lightweight, purpose-built Amazon Q Apps within your broader Amazon Q Business application environment, you must include the following policy permissions for Q Apps.

QAppsResourceAgnosticPermissions
AppsAppUniversalPermissions
QAppsAppOwnerPermissions
QAppsPublishedAppPermissions
QAppsAppSessionModeratorPermissions
QAppsSharedAppSessionPermissions


