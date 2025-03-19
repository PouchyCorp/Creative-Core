#Projet : Creative Core
#Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil

import math
import pygame as pg

root = (300,300)
target = (400,400)
length1 = 400
length2 = 200

rect_surf1 = pg.Surface((length1, 10), pg.SRCALPHA)
pg.draw.rect(rect_surf1, "red", (0,0,length1, 10))
rect_surf2 = pg.Surface((length2, 10), pg.SRCALPHA)
pg.draw.rect(rect_surf2, "green", (0,0,length2, 10))

def point_rotate(image, origin, pivot, angle):
    image_rect = image.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
    offset_center_to_pivot = pg.math.Vector2(origin) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
    rotated_image = pg.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    return rotated_image, rotated_image_rect

def inverse_kinematics(target, root, length1, length2):
    """ Compute the angles needed to reach the target using 2D inverse kinematics """
    dx = target[0] - root[0]
    dy = target[1] - root[1]
    distance = math.sqrt(dx**2 + dy**2)

    # Constrain target distance
    distance = min(distance, length1 + length2)

    # Compute angle for the second joint using the Law of Cosines
    cos_angle2 = (dx**2 + dy**2 - length1**2 - length2**2) / (2 * length1 * length2)
    angle2 = math.acos(max(-1, min(1, cos_angle2)))  # Clamp cos_angle2 to valid range

    # Compute angle for the first joint using the Law of Sines
    k1 = length1 + length2 * math.cos(angle2)
    k2 = length2 * math.sin(angle2)
    angle1 = math.atan2(dy, dx) - math.atan2(k2, k1)

    # Transform into global angles
    return math.degrees(angle1), math.degrees(angle2 + angle1)

pg.init()
screen = pg.display.set_mode((800, 600))
clock = pg.time.Clock()

angle1 = 0
angle2 = 0

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_p:
                angle1 += 10
            elif event.key == pg.K_o:
                angle1 -= 10
            elif event.key == pg.K_k:
                angle2 += 10
            elif event.key == pg.K_l:
                angle2 -= 10
    
    target = pg.mouse.get_pos()
    
    angle1 , angle2 = inverse_kinematics(target, root, length1, length2)

    rotated_surf, rect = point_rotate(rect_surf1, root, (5,5), -angle1)
    relative_arm_vector = pg.Vector2(length1, 0)
    rotated_arm_vector = relative_arm_vector.rotate(angle1)
    global_end_pos = rotated_arm_vector + pg.Vector2(root)
    rotated_surf2, rect2 = point_rotate(rect_surf2, global_end_pos, (5,5), -angle2)

    screen.fill((255, 255, 255))
    screen.blit(rotated_surf, rect)
    screen.blit(rotated_surf2, rect2)

    pg.draw.circle(screen, "blue", target, 10)

    pg.display.flip()
    clock.tick(60)

pg.quit()