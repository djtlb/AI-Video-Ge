# AWS Deployment Configuration for AI Avatar Video

This document provides instructions for deploying the AI Avatar Video application on AWS using the IPs you've provided.

## EC2 Deployment

If you're deploying to EC2 instances with the following IPs:
- 52.41.36.82
- 54.191.253.12
- 44.226.122.3

### Steps:

1. **SSH into your EC2 instances**:
   ```bash
   ssh -i your-key.pem ec2-user@52.41.36.82
   ```

2. **Clone your repository**:
   ```bash
   git clone https://github.com/yourusername/ai-avatar-video.git
   cd ai-avatar-video
   ```

3. **Install dependencies**:
   ```bash
   sudo yum update -y
   sudo yum install -y python3 python3-pip
   python3 -m pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   # For development
   ./run_standalone.sh
   
   # For production
   ./start_daemon.sh 80
   ```

## Load Balancer Configuration

If you're setting up an AWS Application Load Balancer with these instances:

1. Create a target group with your EC2 instances
2. Configure health checks to `/` path
3. Set up security groups to allow traffic from the load balancer to your instances
4. Configure listeners for HTTP (port 80) and HTTPS (port 443)

## Security Groups

Set up security groups to:
1. Allow inbound traffic on ports 22 (SSH), 80 (HTTP), and 443 (HTTPS)
2. Allow outbound traffic as needed
3. Restrict administrative access to trusted IPs

## AWS Elastic Beanstalk (Alternative)

1. Install the EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize EB application:
   ```bash
   eb init -p python-3.8 ai-avatar-video
   ```

3. Create an environment:
   ```bash
   eb create ai-avatar-video-env
   ```

4. Deploy the application:
   ```bash
   eb deploy
   ```

## Environment Variables

Set these environment variables in AWS:

- `PORT=80`
- `ENVIRONMENT=production`
- `ALLOWED_ORIGINS=*`

## IP Whitelisting

The application now includes IP whitelisting middleware. To use it:

1. The `allowed_ips.conf` file contains your whitelisted IPs
2. The middleware will automatically load this file if it exists
3. Only listed IPs will be allowed to access the application

## Monitoring

Set up CloudWatch for monitoring:

1. Install CloudWatch agent on your EC2 instances
2. Configure metrics for CPU, memory, and disk usage
3. Set up alarms for high resource utilization
4. Enable logging to CloudWatch Logs

## Backup Strategy

1. Set up automatic database backups using AWS Backup
2. Configure S3 lifecycle policies for media storage
3. Create AMIs of your configured instances

## Troubleshooting

If you encounter issues:
1. Check CloudWatch Logs
2. Verify security group settings
3. Ensure your application is running (use `systemctl status` if set up as a service)
4. Validate that your IPs are correctly configured in the allowed_ips.conf file
