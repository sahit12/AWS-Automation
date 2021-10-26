## Security Group
* Security Groups acts a virtual firewall between your EC2 instances that control inbound and outbound traffic.
* Security Groups are defined under a Virtual Private Cloud(VPC) in each avaliable regions which a user can use.
* Only unique security groups can be created under each VPCs.
* By default, when one creates an AWS account, they are assigned a default VPC in each available regions. Hence, it isn't generally required to create a VPC unless additional fine tunings need to accompanied in the VPC.
* By default, each default VPC will also contain a default security group. If you don't specify a security group when you launch an instance, the instance is launched into the appropriate default security group.
* A default security group includes a default rule that grants instances unrestricted network access to each other.
* You can add or remove rules from your security groups using `AuthorizeSecurityGroupIngress`, `AuthorizeSecurityGroupEgress`, `RevokeSecurityGroupIngress` and `RevokeSecurityGroupEgress`

## Quotas available (Limits)

| Name | Default | Adjustable |
| ---- | ------- | ---------- |
| VPCs per Region |	5 |	Yes |
| Subnets per VPC |	200 | Yes |
| IPv4 CIDR blocks per VPC | 5 | Yes (up to 50) |
| IPv6 CIDR blocks per VPC | 1 | No |

### DNS

Each EC2 instance can send 1024 packets per second per network interface to Route 53 Resolver (specifically the .2 address, such as 10.0.0.2, and 169.254.169.253). This quota cannot be increased. The number of DNS queries per second supported by Route 53 Resolver varies by the type of query, the size of the response, and the protocol in use. **(AWS Docs)**

### Elastic IP addresses (IPv4)
| Name | Default | Adjustable | Comments |
| ---- | ------- | ---------- | -------- |
| Elastic IP addresses per Region |	5 |	Yes | This quota applies to individual AWS account VPCs and shared VPCs. |

### Security groups

| Name | Default | Adjustable | Comments |
| ---- | ------- | ---------- | -------- |
| VPC security groups per Region | 2,500 | Yes | This quota applies to individual AWS account VPCs and shared VPCs. If you increase this quota to more than 5,000 security groups in a Region, It is recommend that you paginate calls to describe your security groups for better performance. |
| Inbound or outbound rules per security group | 60 | Yes | You can have 60 inbound and 60 outbound rules per security group (making a total of 120 rules). This quota is enforced separately for IPv4 rules and IPv6 rules; for example, a security group can have 60 inbound rules for IPv4 traffic and 60 inbound rules for IPv6 traffic. A quota change applies to both inbound and outbound rules. This quota multiplied by the quota for security groups per network interface cannot exceed 1,000. For example, if you increase this quota to 100, we decrease the quota for your number of security groups per network interface to 10. |
| Security groups per network interface | 5 | Yes (up to 16) | This quota is enforced separately for IPv4 rules and IPv6 rules. The quota for security groups per network interface multiplied by the quota for rules per security group cannot exceed 1,000. For example, if you increase this quota to 10, we decrease the quota for your number of rules per security group to 100. |

**Note** -> If you to get more information on limits, visit <a href="https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html">here</a>