from .bdbaoc import bdbaoc


def setup(bot):
    bot.add_cog(bdbaoc(bot))