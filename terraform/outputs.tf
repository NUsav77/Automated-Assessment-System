// Will provide outputs from the action.
output "light_sail_server_ip" {
  value       = aws_lightsail_static_ip.server_ip.ip_address
  description = "The ip address of the Django server just provisioned"
}