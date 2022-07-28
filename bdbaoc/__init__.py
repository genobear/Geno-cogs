from .bdbaoc import bdbaoc


def setup(bot):
    n = bdbaoc(bot)
    #bot.add_listener(n.on_member_join,"on_member_join")
    bot.add_cog(n)
    