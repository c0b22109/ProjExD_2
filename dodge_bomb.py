import os
import sys
import pygame as pg
import random
import time
import math


WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_imgs = get_kk_imgs()
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.center = [random.randint(10, WIDTH - 10), random.randint(10, HEIGHT - 10)]
    vx = 5
    vy = 5
    clock = pg.time.Clock()
    tmr = 0
    DELTA = {
        pg.K_UP: (0, -5), 
        pg.K_DOWN: (0, 5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (5, 0)
    }

    (bb_img_lst, bb_accs) = init_bb_imgs()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for (key, move)  in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += move[0]
                sum_mv[1] += move[1]


        (vx, vy) = calc_orientation(bb_rct, kk_rct, (vx, vy))

        bb_rct.move_ip(vx * bb_accs[min(tmr // 500, 9)], vy * bb_accs[min(tmr // 500, 10)])
        bb_img = bb_img_lst[min(tmr // 500, 9)]
        tmp_bb_center = bb_rct.center
        bb_rct = bb_img.get_rect()
        bb_rct.center = tmp_bb_center
        bb_bound = check_bound(bb_rct)
        if not bb_bound[0][0] or not bb_bound[0][1]:
            vx *= -1
            if not bb_bound[0][0]:
                bb_rct.left = 0
            else:
                bb_rct.right = WIDTH
        if not bb_bound[1][0] or not bb_bound[1][1]:
            vy *= -1
            if not bb_bound[1][0]:
                bb_rct.top = 0
            else:
                bb_rct.bottom = HEIGHT
        screen.blit(bb_img, bb_rct)

        if sum_mv != [0, 0]:
            kk_img = kk_imgs[tuple(sum_mv)]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != ((True, True), (True, True)):
            kk_rct.move_ip((-sum_mv[0], -sum_mv[1]))
        screen.blit(kk_img, kk_rct)

        pg.display.update()

        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return 0

        tmr += 1
        clock.tick(50)


def check_bound(rct: pg.rect) -> tuple[tuple[bool, bool], tuple[bool, bool]]:
    """
    画面内外判定を行う関数

    引数 
    rct pg.rect: 判定を行うrect

    戻り値
    tuple[tuple[bool, bool], tuple[bool, bool]]: tuple[tuple[左の判定 bool, 右の判定 bool], tuple[上の判定bool, 下の判定 bool]]
    """
    global WIDTH, HEIGHT
    in_window = [[True, True], [True, True]]
    if rct.left < 0:
        in_window[0][0] = False
    if rct.right > WIDTH:
        in_window[0][1] = False
    if rct.top < 0:
        in_window[1][0] = False
    if rct.bottom > HEIGHT:
        in_window[1][1] = False

    return (tuple(in_window[0]), tuple(in_window[1]))


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面の描画を行う関数

    引数
    screen pg.Surface:  ゲームオーバー画面を描画するスクリーン

    戻り値
    なし
    """
    global WIDTH, HEIGHT

    black_out_sf = pg.Surface((WIDTH, HEIGHT))
    black_out_sf.set_alpha(192)
    
    font_obj = pg.font.Font(None, 50)
    txt = font_obj.render("Game Over", True, (255, 255, 255))
    txt_pos_x = black_out_sf.get_width() / 2 - txt.get_width() / 2
    txt_pos_y = black_out_sf.get_height() / 2 - txt.get_height() / 2

    black_out_sf.blit(txt, (txt_pos_x, txt_pos_y))
    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk_img_pos_y = black_out_sf.get_height() / 2 - kk_img.get_height() / 2
    black_out_sf.blit(kk_img, (txt_pos_x - kk_img.get_width() - 10, kk_img_pos_y))
    black_out_sf.blit(kk_img, (black_out_sf.get_width() - txt_pos_x + 10, kk_img_pos_y))

    screen.blit(black_out_sf, (0, 0))
    pg.display.update()
    time.sleep(5)
    

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    爆弾のsurfaceと速度倍率のlistを含むtupleを作成する関数

    引数
    なし

    戻り値
    tuple[list[pg.Surface], list[int]]: tuple[list[異なるサイズの爆弾 pg.Surface], list[爆弾の速度倍率 int]]
    """
    bb_img_lst = []
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_img.set_colorkey((0, 0, 0))
        bb_img_lst.append(bb_img)

    return (bb_img_lst, [a for a in range(1, 11)])


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量をキーとするこうかとんの画像Surfaceのdictを作成する関数

    引数
    なし

    戻り値
    dict[tuple[int, int], pg.Surface]: dict[tuple[横方向の移動量 int, 縦方向の移動量 int], 向きの異なるこうかとんの画像 pg.Surface]
    """
    kk_img = pg.image.load("fig/3.png")
    kk_dict = {(i * 5, j * 5): pg.transform.rotozoom(kk_img, j * 45, 0.9) \
        if i < 0 else pg.transform.rotozoom(pg.transform.flip(kk_img, True, False), j * -90 - 45 * i * -j, 0.9) \
        for i in range(-1, 2) for j in range(-1, 2) if not(i == 0 and j == 0)}
    #kk_dict[(5, 0)] = pg.transform.rotozoom(pg.transform.flip(kk_img, True, False), 0, 0.9)

    return kk_dict


def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    vector_x = dst.centerx - org.centerx
    vector_y = dst.centery - org.centery
    norm = math.sqrt(pow(vector_x, 2) + pow(vector_y, 2))

    if norm >= 300:
        power = math.sqrt(25) / norm
        return (vector_x * power, vector_y * power)
    else:
        return current_xy


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
