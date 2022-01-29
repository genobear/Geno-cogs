from .bdb import bdb


def setup(bot):
    bot.add_cog(bdb(bot))