from .bdbdev import bdbdev


def setup(bot):
    bot.add_cog(bdbdev(bot))