import re

spaces = [
    "cozy",
    "medium-sized",
    "spacious",
    "massive"
]

items = [
    "bookshelves",
    "fireplaces",
    "suits",
    "tables",
    "chests",
    "beds",
    "paintings",
    "statues",
    "tapestries",
    "candelabras",
    "chairs",
    "fountains",
    "mirrors",
    "rugs",
    "curtains",
    "chess",
]

styles = [
    "Art",
    "Baroque",
    "Classical",
    "Colonial",
    "Contemporary",
    "Country",
    "Gothic",
    "Industrial",
    "Mediterranean",
    "Minimalist",
    "Neoclassical",
    "Renaissance",
    "Rococo",
    "Romantic",
    "Rustic",
    "Victorian",
]



sample = "As you step into the room, you find yourself standing in a cozy space. The walls are adorned with beds and a two large curtains dominate the center of the room. You see 21 flowers in a vase, and through a window you stop to count 78805 stars. The room appears well designed in the Baroque style."


def decode_description(description):
    consumed = 0

    space_size = description[59:].split(" ")[0]
    space_value = spaces.index(space_size)
    print(f"{space_size=}, {space_value=}")
    consumed = 59 + len(space_size)

    item1 = description[consumed + 35:].split(" ")[0]
    item1_value = items.index(item1)
    print(f"{item1=}, {item1_value=}")
    consumed += 35 + len(item1)

    if item1 == "suits":
        consumed += 9
    
    if item1 == "chess":
        consumed += 5

    item2 = description[consumed + 17:].split(" ")[0]
    item2_value = items.index(item2)
    print(f"{item2=}, {item2_value=}")
    consumed += 17 + len(item2)

    if item2 == "suits":
        consumed += 9
    
    if item2 == "chess":
        consumed += 5

    flowers = description[consumed + 42:].split(" ")[0]
    print(f"{flowers=}")
    consumed += 42 + len(flowers)

    stars = description[consumed + 59:].split(" ")[0]
    print(f"{stars=}")
    consumed += 59 + len(stars)

    style = description[consumed + 46:].split(" ")[0]
    style_value = styles.index(style)
    print(f"{style=}, {style_value=}")
    consumed += 46 + len(style)
    if style == "Art":
        consumed += 5


    # spaces[(int)(rand_int & 3)] -> gives least significant 2 bits
    # items[(int)((uint)(rand_long >> 2) & 0xf)] -> gives us bits 2-6
    # items[(int)((uint)(rand_long >> 6) & 0xf)] -> gives us bits 7-8
    # flowers: (ulong)((uint)(rand_long >> 0xe) & 0x1f)
    # stars: rand_long >> 0xe & 0xffffffff,
    # styles[(int)((uint)(rand_long >> 10) & 0xf)]

    val = (int(flowers) << 0xe) | (int(stars) << 0xe) | (style_value << 10) | (item2_value << 6) | (item1_value << 2) | (space_value)

    print("{0:b}".format(val))
    print(val)
    print(hex(val))
    return val
