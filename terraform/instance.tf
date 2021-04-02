// Associate the ip address to the instance.
resource "aws_lightsail_static_ip_attachment" "test" {
  static_ip_name = aws_lightsail_static_ip.server_ip.id
  instance_name  = aws_lightsail_instance.server.id
}

// Static ip address
resource "aws_lightsail_static_ip" "server_ip" {
  name = "Django-static-ip"
}



// Lightsail instance we should run and where.
resource "aws_lightsail_instance" "server" {
  name              = "Django"
  availability_zone = "us-west-2a"
  blueprint_id      = "ubuntu_20_04"
  bundle_id         = "nano_2_0"
  user_data         = data.template_file.foo.rendered

}

// a bash script that can have secrets added.
data "template_file" "foo" {
  template = file("boot.sh.tpl")
  vars = {
    SECRET = var.SECRET_KEY
  }

}

// lightsail SSH key we should use.
resource "aws_lightsail_key_pair" "ls_key_pair" {
  name       = "importing"
  public_key = var.ssh_pub_key
}
