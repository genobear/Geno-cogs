from .bdbdev import bdbdev


async def setup(bot):
    bot.add_cog(bdbdev(bot))
