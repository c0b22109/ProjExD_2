import os
import sys
import random
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA: dict = {
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, 5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (5, 0)        
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数: こうかとん、または爆弾のRect
    戻り値: 真理値タプル (横判定結果, 縦判定結果)
    画面内ならTrue 画面外ならFalse
    """

    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    
    return (yoko, tate)


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (bb_img.get_width() / 2, bb_img.get_height() / 2), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
    bb_vx = 5
    bb_vy = 5
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0])

        if kk_rct.colliderect(bb_rct):
            draw_gameover(screen)
            return

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for tpl in DELTA.items():
            if key_lst[tpl[0]]:
                sum_mv[0] += tpl[1][0]
                sum_mv[1] += tpl[1][1]

        kk_rct.move_ip(sum_mv)
        bb_rct.move_ip(bb_vx, bb_vy)

        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        check_res = check_bound(bb_rct)
        if not check_res[0]:
            bb_vx *= -1
        if not check_res[1]:
            bb_vy *= -1

        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


def draw_gameover(screen: pg.Surface):
    """
    引数: 描画するスクリーン
    戻り値: なし
    ゲームオーバー画面を描画する関数
    """
    fnt = pg.font.Font(None, 100) #  フォントサイズを100に設定

    black_out = pg.Surface((WIDTH, HEIGHT)) #  ブラックアウトSurfaceを生成
    pg.draw.rect(black_out, (0, 0, 0), (0, 0, WIDTH, HEIGHT)) #  画面サイズと同じ四角形を生成
    black_out.set_alpha(128) #  透過度を50%に設定

    txt = fnt.render("Game Over", True, (255, 255, 255)) #  "Game Over"テキストのSurfaceを生成
    txt_and_center_diff = txt.get_width() / 2 #  画面の中心座標とテキストの端の座標のずれを計算

    kk_img_cry = pg.image.load("fig/8.png") #  ないているこうかとんの画像Surfaceを生成

    screen.blit(black_out, (0, 0)) #  ブラックアウトを描画
    screen.blit(txt, (WIDTH / 2 - txt_and_center_diff, HEIGHT / 2 - txt.get_height() / 2)) #  画面の中心にテキストが来るよう、描画
    screen.blit(kk_img_cry, (WIDTH / 2 - txt_and_center_diff - kk_img_cry.get_width() - 10, HEIGHT / 2 - kk_img_cry.get_height() / 2)) #  テキストの右端-10pxにこうかとんの画像を描画
    screen.blit(kk_img_cry, (WIDTH / 2 + txt_and_center_diff + 10, HEIGHT / 2 - kk_img_cry.get_height() / 2)) #  テキストの左端+10pxにこうかとんの画像を描画
    pg.display.update() #  画面を更新
    time.sleep(5) #  5秒待機
    return


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
