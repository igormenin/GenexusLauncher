from PIL import Image, ImageDraw

def generate_icons():
    size = (20, 20)
    color = (51, 51, 51, 255) # Dark gray
    
    # Plus Icon
    img_plus = Image.new('RGBA', size, (255, 255, 255, 0))
    draw_plus = ImageDraw.Draw(img_plus)
    # Draw a circle plus
    draw_plus.ellipse([2, 2, 17, 17], outline=color, width=2)
    draw_plus.line([10, 6, 10, 13], fill=color, width=2)
    draw_plus.line([6, 10, 14, 10], fill=color, width=2)
    img_plus.save("plus.png")
    
    # Delete Icon (Trash)
    img_del = Image.new('RGBA', size, (255, 255, 255, 0))
    draw_del = ImageDraw.Draw(img_del)
    # Draw a bin
    draw_del.rectangle([5, 6, 14, 17], outline=color, width=2)
    draw_del.line([3, 5, 16, 5], fill=color, width=2)
    draw_del.line([8, 2, 11, 2], fill=color, width=2)
    # Vertical lines in the bin
    draw_del.line([8, 8, 8, 15], fill=color, width=1)
    draw_del.line([11, 8, 11, 15], fill=color, width=1)
    img_del.save("delete.png")

if __name__ == "__main__":
    generate_icons()
