# Amazon Q Business Roles CloudFormation Template

Users with admin roles are able to create new resources on their AWS Accounts. However, there will be situations where the person creating Q Business resources doesn’t have an admin role. Thus, we have to make sure this person has the right permissions following the least-privileged principle.

This CloudFormation template is designed to create three IAM roles specifically tailored for managing and operating Amazon Q Business applications. These roles provide the necessary permissions to streamline the process of setting up and administering Q Business applications within your AWS environment.

> [!CAUTION] 
> Please note that this CloudFormation template is provided as a starting point and is not intended for direct use in production environments without further modifications. The roles created by this template, especially the "qbusinessDatasourceRole," may require additional adjustments to accommodate specific data connectors and use cases. It is crucial to review and customize the roles based on your organization's security requirements and the specific needs of your Amazon Q Business applications.

We recommend thoroughly testing and refining the roles in a non-production environment before applying them to your production setup. Ensure that the roles align with your security best practices and grant only the minimum necessary permissions for your Q Business applications to function effectively.


## Roles Created by the Template

1. **qbusinessblueprint**: This role is intended to be assumed by the person responsible for operating Amazon Q Business applications. It grants permissions to perform essential tasks such as creating applications, adding users to applications, modifying subscriptions, and more. By assuming this role, the designated operator can efficiently manage and maintain the Q Business application ecosystem.

2. **qbusinessDatasourceRole**: This role is designed to be assigned to every data source created within Amazon Q Business applications. It provides the necessary permissions for the data source to access and interact with relevant AWS services and resources. Assigning this role to your data sources ensures that they have the required access to function properly within the Q Business environment.

3. **qbusinessWebRole**: This role is meant to be assigned to the web experience created during the final step of setting up an Amazon Q Business application. It grants the necessary permissions for the web experience to interact with the Q Business application and perform its intended functions seamlessly.





## Getting Started

To use this CloudFormation template, follow these steps:

1. Review the template and make any necessary adjustments to fit your specific requirements.
2. Deploy the CloudFormation stack using this template in your desired AWS environment.
3. Assign the "qbusinessblueprint" role to the person responsible for operating your Q Business applications.
4. When creating data sources for your Q Business applications, assign the "qbusinessDatasourceRole" to each data source.
5. During the final step of creating a Q Business application, assign the "qbusinessWebRole" to the web experience.

By leveraging this CloudFormation template, you can quickly set up the essential roles needed to manage and operate your Amazon Q Business applications, saving time and effort in the process.