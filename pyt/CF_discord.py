import discord
from discord.ext import commands
import requests
import tabulate

intents = discord.Intents.default()
intents.all()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Cloudflare API configuration
CF_API_BASE_URL = "https://api.cloudflare.com/client/v4"
CF_API_TOKEN = "XXXX"
CF_API_KEY = "XXXX"
CF_API_EMAIL = "xxx@xxx.com"
#embed.set_thumbnail(url="https://toppng.com/uploads/preview/cloudflare-logo-vector-11573946103zsbxw5kpaj.png")

def get_all_zones():
    api_endpoint = f"{CF_API_BASE_URL}/zones"

    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Email': CF_API_EMAIL,
        'X-Auth-Key': CF_API_KEY,
    }

    response = requests.get(api_endpoint, headers=headers)

    if response.status_code == 200:
        return response.json().get('result', [])
    else:
        return None

# Function to get detailed information about a Cloudflare zone
def get_zone_info(zone_id):
    api_endpoint = f"{CF_API_BASE_URL}/zones/{zone_id}"

    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Email': CF_API_EMAIL,
        'X-Auth-Key': CF_API_KEY,
    }

    response = requests.get(api_endpoint, headers=headers)

    if response.status_code == 200:
        return response.json().get('result', {})
    else:
        return None

# Function to get detailed information about a Cloudflare user
def get_user_info():
    api_endpoint = f"{CF_API_BASE_URL}/user"

    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Email': CF_API_EMAIL,
        'X-Auth-Key': CF_API_KEY,
    }

    response = requests.get(api_endpoint, headers=headers)

    if response.status_code == 200:
        return response.json().get('result', {})
    else:
        return None

# Function to get Zone IDs for a given domain
def get_zone_ids(domain):
    api_endpoint = f"{CF_API_BASE_URL}/zones"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CF_API_TOKEN}'
    }

    response = requests.get(api_endpoint, headers=headers)

    if response.status_code == 200:
        zones = response.json().get('result', [])
        return [zone['id'] for zone in zones if domain.endswith(zone['name'])]

    return []
    
# Function to update a DNS record
def update_dns_record(zone_id, record_id, record_type, content):
    api_endpoint = f"{CF_API_BASE_URL}/zones/{zone_id}/dns_records/{record_id}"

    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Email': CF_API_EMAIL,
        'X-Auth-Key': CF_API_KEY,
    }

    data = {
        'type': record_type,
        'content': content,
    }

    response = requests.put(api_endpoint, headers=headers, json=data)

    return response

# Help command
@bot.command()
async def help_dns (ctx):
    help_message = """
    **Available DNS Commands:**
    - `!list_domains <domain>`: List detailed information about all zones matching the specified domain.
    - `!list_dns <domain>`: List all DNS records for the specified domain.
    - `!add_dns <domain> <record_type> <content>`: Add a new DNS entry.
    - `!update_dns <domain> <record_type> <content>`: Update an existing DNS entry.
    - `!delete_dns <domain>`: Delete a DNS entry for the specified domain.
    
    **Example Usage:**
    - `!list_domains example.com`
    - `!list_dns example.com`
    - `!add_dns example.com A 192.168.1.1`
    - `!update_dns example.com A 192.168.1.2`
    - `!delete_dns example.com`
    """
    await ctx.send(help_message)

# Command to list all DNS records for a domain
@bot.command()
async def list_dns(ctx, domain):
    try:
        # Get the Zone ID for the specified domain
        zone_ids = get_zone_ids(domain)

        if not zone_ids:
            await ctx.send(f"Failed to get Zone IDs for {domain}. Make sure the domain is configured in Cloudflare.")
            return

        # Cloudflare API endpoint for listing DNS records
        api_endpoint = f"{CF_API_BASE_URL}/zones/{zone_ids[0]}/dns_records"

        # Prepare headers for API request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {CF_API_TOKEN}'
        }

        # Make API request to list DNS records
        response = requests.get(api_endpoint, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            dns_records = response.json().get('result', [])
            if not dns_records:
                embed = discord.Embed(
                    title=f"No DNS records found for {domain}",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
                return

            # Create a list of lists for tabulated output
            table_data = [['Name', 'Type', 'Content']]
            for record in dns_records:
                table_data.append([record['name'], record['type'], record['content']])

            # Convert the table data to a tabulated string
            table_str = tabulate.tabulate(table_data, headers='firstrow', tablefmt='fancy_grid')

            # Construct an embedded message with the tabulated data
            embed = discord.Embed(
                title=f"DNS records for {domain}",
                description=f"```\n{table_str}\n```",
                color=discord.Color.blue()
            )

            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Failed to get DNS records for {domain}",
                description=f"Error: {response.text}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="An Error Occurred",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Command to list detailed information about all zones matching the specified domain
@bot.command()
async def domain (ctx, domain=None):
    try:
        # Get Zone IDs for the specified domain
        zone_ids = get_zone_ids(domain)

        if not zone_ids:
            # No matching zones found
            embed = discord.Embed(
                title=f"No Matching Zones Found for {domain}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        # Get user information
        user_info = get_user_info()

        # Construct an embedded message with detailed information about each zone
        embed = discord.Embed(
                title=f"{domain}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url="https://toppng.com/uploads/preview/cloudflare-logo-vector-11573946103zsbxw5kpaj.png")

        for zone_id in zone_ids:
            zone_info = get_zone_info(zone_id)
            if zone_info:
                embed.add_field(
                    name=f"Zone: {zone_info['name']}",
                    value=f"Zone ID: {zone_info['id']}\nPlan: {zone_info['plan']['name']}\nUser : {user_info.get('email', 'N/A')}",
                    inline=False
                )

        await ctx.send(embed=embed)

    except Exception as e:
        # An error occurred
        embed = discord.Embed(
            title="An Error Occurred",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Command to list all domains associated with the Cloudflare account
@bot.command()
async def list_domains(ctx):
    try:
        # Get a list of all zones
        all_zones = get_all_zones()

        if not all_zones:
            # No zones found
            embed = discord.Embed(
                title="No Domains Found",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return

        # Construct an embedded message with detailed information about each zone
        embed = discord.Embed(
            title="Domains Associated with the Cloudflare Account",
            color=discord.Color.blue()
        )
        
        embed.set_thumbnail(url="https://toppng.com/uploads/preview/cloudflare-logo-vector-11573946103zsbxw5kpaj.png")

        for zone in all_zones:
            embed.add_field(
                name=f"Domain: {zone['name']}",
                value=f"ID: {zone['id']}\nPlan: {zone['plan']['name']}",
                inline=False
            )

        await ctx.send(embed=embed)

    except Exception as e:
        # An error occurred
        embed = discord.Embed(
            title="An Error Occurred",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Command to add a new DNS entry
@bot.command()
async def add_dns(ctx, domain, record_type, content):
    try:
        # Get the Zone ID for the specified domain
        zone_id = get_zone_ids(domain)
        
        if not zone_id:
            await ctx.send(f"Failed to get Zone ID for {domain}. Make sure the domain is configured in Cloudflare.")
            return

        # Cloudflare API endpoint for adding DNS records
        api_endpoint = f"{CF_API_BASE_URL}/zones/{zone_id[0]}/dns_records"

        # Prepare headers for API request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {CF_API_TOKEN}'
        }

        # Prepare data for DNS record creation
        data = {
            'type': record_type,
            'name': domain,
            'content': content,
            'ttl': 120,  # Adjust TTL as needed
        }

        # Make API request to add DNS record
        response = requests.post(api_endpoint, headers=headers, json=data)

        # Check if the request was successful
        if response.status_code == 200:
            await ctx.send(f"DNS record added successfully for {domain}")
        else:
            await ctx.send(f"Failed to add DNS record. Error: {response.text}")

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Command to update an existing DNS entry
@bot.command()
async def update_dns(ctx, domain, record_type, new_content):
    try:
        # Get the Zone ID for the specified domain
        zone_ids = get_zone_ids(domain)
        
        if not zone_ids:
            await ctx.send(f"Failed to get Zone IDs for {domain}. Make sure the domain is configured in Cloudflare.")
            return

        # Cloudflare API endpoint for listing DNS records
        api_endpoint = f"{CF_API_BASE_URL}/zones/{zone_ids[0]}/dns_records"

        # Prepare headers for API request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {CF_API_TOKEN}'
        }

        # Make API request to list DNS records
        response = requests.get(api_endpoint, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            dns_records = response.json().get('result', [])
            if not dns_records:
                await ctx.send(f"No DNS records found for {domain}.")
                return

            # Find the DNS record to update
            record_to_update = None
            for record in dns_records:
                if record['type'].upper() == record_type.upper() and record['name'] == domain:
                    record_to_update = record
                    break

            if record_to_update:
                # Update the DNS record
                update_response = update_dns_record(zone_ids[0], record_to_update['id'], record_type, new_content)

                # Check if the update was successful
                if update_response.status_code == 200:
                    await ctx.send(f"DNS record updated successfully for {domain}.")
                else:
                    await ctx.send(f"Failed to update DNS record. Update response: {update_response.text}, Zone-ID : {zone_ids}, Details: {new_content}")
            else:
                await ctx.send(f"No matching DNS record found for {domain} with type {record_type}.")
        else:
            await ctx.send(f"Failed to get DNS records. Error: {response.text}")

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Command to delete a DNS entry
@bot.command()
async def delete_dns(ctx, domain):
    try:
        # Get the Zone ID for the specified domain
        zone_ids = get_zone_ids(domain)
        
        if not zone_ids:
            await ctx.send(f"Failed to get Zone IDs for {domain}. Make sure the domain is configured in Cloudflare.")
            return

        # Cloudflare API endpoint for deleting DNS records
        api_endpoint = f"{CF_API_BASE_URL}/zones/{zone_ids[0]}/dns_records"

        # Prepare headers for API request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {CF_API_TOKEN}'
        }

        # Get the DNS record ID for the specified domain
        response = requests.get(api_endpoint, headers=headers)
        if response.status_code == 200:
            dns_records = response.json().get('result', [])
            record_ids = [record['id'] for record in dns_records if record['name'] == domain]

            if not record_ids:
                await ctx.send(f"No DNS records found for {domain}.")
                return

            # Delete each DNS record
            for record_id in record_ids:
                delete_endpoint = f"{api_endpoint}/{record_id}"
                delete_response = requests.delete(delete_endpoint, headers=headers)

                # Check if the request was successful
                if delete_response.status_code == 200:
                    await ctx.send(f"DNS record deleted successfully for {domain}")
                else:
                    await ctx.send(f"Failed to delete DNS record. Error: {delete_response.text}")

        else:
            await ctx.send(f"Failed to get DNS records for Zone ID {zone_ids[0]}. Error: {response.text}")

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Run the bot - bot token
bot.run('XXXXXX')

