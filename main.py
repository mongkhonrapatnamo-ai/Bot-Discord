import os
import discord
from discord.ext import commands
from discord.ui import Modal, Select, TextInput, View
from keep_alive import keep_alive # <--- เพิ่มตรงนี้

keep_alive() # <--- เพิ่มตรงนี้
intents = discord.Intents.default()
intents.message_content = True

intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== ID ต่างๆ (กำหนดเองที่นี่) ====================
BOT_CHANNEL_ID = 1460157801560150056  # ID ช่องบอท (ช่องสำหรับพิมพ์คำสั่ง !setup)
VERIFY_CHANNEL_ID = 1541104532065493113  # ID ช่องยืนยัน (ช่องที่จะให้ปุ่มลงทะเบียนไปโผล่)

# JOIN_CHANNEL_ID = 995002105670672465  # ID ช่องแจ้งเตือนคนเข้า
# LEAVE_CHANNEL_ID = 1460163789507924019  # ID ช่องแจ้งเตือนคนออก
MEMBER_ROLE_ID = 1541105332137361620  # ID ยศสมาชิกทั่วไป

# ID ยศแยกตามช่วงอายุ
AGE_ROLES = {
    "12-15": [1541106503535034408, 1429856682728624138],
    "16-18": [1541107347298975805, 1429856682728624138],
    "19-22": [1541107384825548911, 1429857122014724170],
    "22+": [1541107429989818389, 1429857122014724170],
}


# ==================== 1. ฟอร์มกรอกชื่อ (Modal) ====================
class NameModal(Modal, title="กรอกชื่อของคุณ - Register ( Shark | หลาม )"):
    name_en = TextInput(
        label="ชื่อภาษาอังกฤษ (Eng Name)",
        placeholder="เช่น Shark",
        max_length=30,
    )
    name_th = TextInput(
        label="ชื่อภาษาไทย (Thai Name)",
        placeholder="เช่น หลาม",
        max_length=30,
    )

    async def on_submit(self, interaction: discord.Interaction):
        view = AgeSelectView(
            name_en=self.name_en.value, name_th=self.name_th.value
        )
        await interaction.response.send_message(
            "age :",
            view=view,
            ephemeral=True,
        )


# ==================== 2. เมนูเลือกช่วงอายุ (Select Menu) ====================
class AgeSelect(Select):

    def __init__(self, name_en, name_th):
        self.name_en = name_en
        self.name_th = name_th

        options = [
            discord.SelectOption(
                label="12 - 15 ปี",
                value="12-15",
                description="อายุ 12-15 ปี",
            ),
            discord.SelectOption(
                label="16 - 18 ปี",
                value="16-18",
                description="อายุ 16-18 ปี",
            ),
            discord.SelectOption(
                label="19 - 22 ปี",
                value="19-22",
                description="อายุ 19-22 ปี",
            ),
            discord.SelectOption(
                label="22 ปีขึ้นไป (22+)",
                value="20+",
                description="อายุ 20 ปีขึ้นไป",
            ),
        ]
        super().__init__(
            placeholder="คลิกเพื่อเลือกช่วงอายุ...",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        selected_age = self.values[0]

        # เปลี่ยนชื่อเล่น
        new_nickname = f"{self.name_en} | {self.name_th}"
        try:
            await user.edit(nick=new_nickname[:32])
        except discord.Forbidden:
            pass

        # แจกยศสมาชิกทั่วไป
        member_role = interaction.guild.get_role(MEMBER_ROLE_ID)
        if member_role:
            await user.add_roles(member_role)

        # แจกยศตามช่วงอายุ
        role_ids = AGE_ROLES.get(selected_age, [])
        for r_id in role_ids:
            role = interaction.guild.get_role(r_id)
            if role:
                await user.add_roles(role)

        await interaction.response.edit_message(
            content=f"ลงทะเบียนสำเร็จ! เปลี่ยนชื่อเป็น `{new_nickname[:32]}` และได้รับยศช่วงอายุ `{selected_age}` เรียบร้อยแล้วครับ",
            view=None,
        )


class AgeSelectView(View):

    def __init__(self, name_en, name_th):
        super().__init__(timeout=180)
        self.add_item(AgeSelect(name_en, name_th))


# ==================== 3. ปุ่มกดเริ่มต้น ====================
class RegisterView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="ลงทะเบียนเข้าเซิร์ฟเวอร์",
        style=discord.ButtonStyle.green,
        custom_id="reg_btn",
    )
    async def register_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(NameModal())


# ==================== EVENT & COMMANDS ====================
@bot.event
async def on_ready():
    print(f"บอทพร้อมทำงานแล้ว: {bot.user}")
    bot.add_view(RegisterView())


# @bot.event
# async def on_member_join(member):
#     channel = member.guild.get_channel(JOIN_CHANNEL_ID)
#     if channel:
#         # 1. สร้าง Embed และตั้งค่าสีแถบข้าง (เช่น สีฟ้า)
#         embed = discord.Embed(
#             title=f"ประตูมิติเบื้องหน้าเปิดออก...\nยินดีต้อนรับนักผจญภัย {member.guild.name}",
#             description=f"ที่นี่คือจุดเริ่มต้นของผู้ถูกอัญเชิญทุกคนก่อนออกเดินทางในโลก {member.guild.name} โปรดแนะนำตัวเพื่อให้โลกใบนี้จดจำการมีอยู่ของคุณ",
#             color=discord.Color.blue(),
#         )

#         # 2. ใส่ Author (ชื่อสมาชิก + รูปโปรไฟล์เล็กๆ ด้านซ้ายบน)
#         embed.set_author(
#             name=member.name, icon_url=member.display_avatar.url
#         )

#         # 3. ใส่ Thumbnail (รูปโปรไฟล์สมาชิกขวาบน)
#         embed.set_thumbnail(url=member.display_avatar.url)

#         # 4. ใส่ Image ด้านล่าง (ใส่ URL รูปภาพหรือ GIF ต้อนรับ)
#         embed.set_image(url="https://i.redd.it/gura-gifs-v0-9jltukzt6mge1.gif?width=498&auto=webp&s=0fd856ba5c6d22d2069847a978600071d0a804d3")

#         # 5. ส่งข้อความพร้อมแท็กชื่อสมาชิกใน content
#         # await channel.send(
#         #     content=f"ผู้ถูกอัญเชิญ {member.mention}!", embed=embed
#         # )

# @bot.event
# async def on_member_remove(member):
#     channel = member.guild.get_channel(LEAVE_CHANNEL_ID)
#     if channel:
#         # 1. สร้าง Embed และตั้งค่าสีแถบข้าง (เช่น สีฟ้า)
#         embed = discord.Embed(
#             title=f"สิ้นสุดภารกิจ {member.display_name} ได้ออกจากโลก {member.guild.name}",
#             description=f"Quest นี้ได้สิ้นสุดแล้ว\nผู้เล่นกำลังออกจากโลก {member.guild.name} ขอให้การผจญภัยครั้งต่อไปของคุณราบรื่น",
#             color=discord.Color.blue(),
#         )

#         # 2. ใส่ Author (ชื่อสมาชิก + รูปโปรไฟล์เล็กๆ ด้านซ้ายบน)
#         embed.set_author(
#             name=member.name, icon_url=member.display_avatar.url
#         )

#         # 3. ใส่ Thumbnail (รูปโปรไฟล์สมาชิกขวาบน)
#         embed.set_thumbnail(url=member.display_avatar.url)

#         # 4. ใส่ Image ด้านล่าง (ใส่ URL รูปภาพหรือ GIF ต้อนรับ)
#         embed.set_image(url="https://media.tenor.com/kVh-wkmgcV4AAAAM/gawr-gura-gura.gif")
        
#         # 5. ส่งข้อความพร้อมแท็กชื่อสมาชิกใน content
#         # await channel.send(
#         #     content=f"ผู้ถูกอัญเชิญ {member.mention}!", embed=embed
#         # )


# คำสั่งพิมพ์สร้างปุ่ม
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    # ตรวจสอบว่าพิมพ์คำสั่งในช่องบอทหรือไม่
    if ctx.channel.id != BOT_CHANNEL_ID:
        await ctx.send(
            f"กรุณาใช้คำสั่งนี้ในช่อง <#{BOT_CHANNEL_ID}> เท่านั้น!",
            delete_after=5,
        )
        return

    # ดึงข้อมูลช่องยืนยันตัวตน
    verify_channel = ctx.guild.get_channel(VERIFY_CHANNEL_ID)
    if not verify_channel:
        await ctx.send("ไม่พบช่องยืนยันตัวตน กรุณาตรวจสอบ ID ช่องอีกครั้ง")
        return

    embed = discord.Embed(
        title="ลงทะเบียนเข้าใช้งาน",
        description="กรุณากดปุ่มด้านล่างเพื่อกรอกชื่อและเลือกช่วงอายุ",
        color=discord.Color.blue(),
    )

    # ส่งปุ่มลงทะเบียนไปยังห้องยืนยันตัวตน
    await verify_channel.send(embed=embed, view=RegisterView())
    await ctx.send(
        f"สร้างปุ่มลงทะเบียนในช่อง <#{VERIFY_CHANNEL_ID}> เรียบร้อยแล้ว!"
    )

bot.run(os.environ.get("MTU0MDgxNTk4MzE3Mjc4ODM0Ng.GDTbrs.Jekrpw0XDfN0-uCiTqz0ggeYU-QhgHYpl9DRGw"))
