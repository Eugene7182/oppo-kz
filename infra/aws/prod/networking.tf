resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(local.tags, {
    Name = "${var.project}-${var.environment}-vpc"
  })
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.tags, { Name = "${var.project}-${var.environment}-igw" })
}

resource "aws_subnet" "public" {
  for_each = zipmap(range(length(var.public_subnet_cidrs)), var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = each.value
  map_public_ip_on_launch = true
  availability_zone       = element(data.aws_availability_zones.available.names, each.key)

  tags = merge(local.tags, {
    Name = "${var.project}-${var.environment}-public-${each.key}"
    Tier = "public"
  })
}

resource "aws_subnet" "private" {
  for_each = zipmap(range(length(var.private_subnet_cidrs)), var.private_subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = element(data.aws_availability_zones.available.names, each.key)

  tags = merge(local.tags, {
    Name = "${var.project}-${var.environment}-private-${each.key}"
    Tier = "private"
  })
}

resource "aws_subnet" "database" {
  for_each = zipmap(range(length(var.database_subnet_cidrs)), var.database_subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = element(data.aws_availability_zones.available.names, each.key)

  tags = merge(local.tags, {
    Name = "${var.project}-${var.environment}-db-${each.key}"
    Tier = "database"
  })
}

resource "aws_eip" "nat" {
  for_each = aws_subnet.public

  domain = "vpc"

  tags = merge(local.tags, { Name = "${var.project}-${var.environment}-nat-eip-${each.key}" })
}

resource "aws_nat_gateway" "this" {
  for_each = aws_subnet.public

  allocation_id = aws_eip.nat[each.key].id
  subnet_id     = each.value.id

  tags = merge(local.tags, { Name = "${var.project}-${var.environment}-nat-${each.key}" })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.tags, { Name = "${var.project}-${var.environment}-public" })
}

resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this.id
}

resource "aws_route_table_association" "public" {
  for_each       = aws_subnet.public
  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  for_each = aws_nat_gateway.this

  vpc_id = aws_vpc.main.id

  tags = merge(local.tags, { Name = "${var.project}-${var.environment}-private-${each.key}" })
}

resource "aws_route" "private_internet" {
  for_each = aws_nat_gateway.this

  route_table_id         = aws_route_table.private[each.key].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = each.value.id
}

resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private[each.key].id
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.project}-${var.environment}-db-subnet"
  subnet_ids = [for s in aws_subnet.database : s.id]

  tags = merge(local.tags, { Name = "${var.project}-${var.environment}-db-subnet" })
}

data "aws_availability_zones" "available" {
  state = "available"
}
