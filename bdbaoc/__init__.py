from .bdbaoc import bdbaoc


def setup(bot):
    n = bdbaoc(bot)
    #bot.add_listener(n.scan_on_join,"on_member_join")
    bot.add_cog(n)
    