# Discord bot for Cloudflare basic DNS management

# How to start
1. Edit CF_discord.py with the required token.
2. Start the container using docker-compose
3. Once the container started, the bot should be online and can run DNS command.

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
