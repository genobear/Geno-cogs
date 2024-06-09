from .bdbdev import bdbdev


async def setup(bot):
    await bot.add_cog(bdbdev(bot))
