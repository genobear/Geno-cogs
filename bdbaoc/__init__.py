from .bdbaoc import bdbaoc


async def setup(bot):
    n = bdbaoc(bot)
    # bot.add_listener(n.on_member_join,"on_member_join")
    await bot.add_cog(n)
