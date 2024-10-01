import os
import sys
import math
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
    kk_img_dict = make_kk_img_dict() #  こうかとんの画像辞書を作成
    kk_img: pg.Surface = kk_img_dict[(5, 0)] #  右向きのこうかとんを初期画像に設定
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_accs_lst, bb_img_lst = make_bomb_list() #  タプルを展開
    bb_img: pg.Surface = bb_img_lst[0] #  最初の爆弾で初期化
    bb_rct = bb_img.get_rect()
    bb_rct.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
    bb_vx = 5
    bb_vy = 5
    clock = pg.time.Clock()
    tmr = 0
    while True:
        bb_acc = bb_accs_lst[min(tmr // 500, 9)] #  タイマー500カウントごとに加速度を変更
        bb_img = bb_img_lst[min(tmr // 500, 9)] #  タイマー500カウントごとに爆弾のサイズを変更

        bb_vx, bb_vy = chase_bomb(kk_rct, bb_rct, bb_vx, bb_vy) #  こうかとんと爆弾の中心座標から爆弾の移動量を計算

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
        bb_rct.move_ip(bb_vx * bb_acc, bb_vy * bb_acc) #  加速度を含んだ移動量で移動

        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        check_res = check_bound(bb_rct)
        if not check_res[0]:
            bb_vx *= -1
        if not check_res[1]:
            bb_vy *= -1

        screen.blit(kk_img_dict[tuple(sum_mv)], kk_rct) #  移動量をキーとして辞書から描画画像を選択
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


def make_bomb_list() -> tuple[list, list]:
    """
    引数: なし
    戻り値: 加速度のリストと爆弾Surfaceのリストのタプル
    加速度リストとサイズの違う爆弾Surfaceのリストを作成する関数
    """
    accs = [a for a in range(1, 11)] #  加速度のリストを作成
    bomb_Surface = []
    for r in range(1, 11): #  爆弾を10種類作成
        bb_img = pg.Surface((20 * r, 20 * r))
        pg.draw.circle(bb_img, (255, 0, 0), (bb_img.get_width() / 2, bb_img.get_height() / 2), 10 * r)
        bb_img.set_colorkey((0, 0, 0))
        bomb_Surface.append(bb_img) #  リストに追加

    return (accs, bomb_Surface) #  タプルを返却


def make_kk_img_dict() -> dict[tuple[int, int]: pg.Surface]:
    """
    引数: なし
    戻り値: 移動量のタプルをキーとした、こうかとん画像の辞書
    押下キーに対する移動量の合計値タプルをキーとした、こうかとんの回転画像の辞書を作成する関数
    """
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9) #  こうかとんの画像をロード

    #左右への移動量が0の場合、左の場合、右の場合に分けて辞書を作成
    kk_img_dict: dict = {
        (i * 5, j * 5): pg.transform.flip(pg.transform.rotozoom(kk_img, 90 * j, 1), True, False) if i == 0 \
        else pg.transform.flip(pg.transform.rotozoom(kk_img, 45 * j, 1), True, False) if i >= 0 \
        else pg.transform.rotozoom(kk_img, 45 * j, 1) for i in range(-1, 2) for j in range(-1, 2)
    }   #移動量の合計値をキーとするこうかとんの画像Surfaceの辞書を作成

    return kk_img_dict

def chase_bomb(kk_rct: pg.Rect, bb_rct: pg.Rect, vx: float, vy: float) -> tuple[float, float]:
    """
    引数: こうかとんのRect, 爆弾のRect, 直前の爆弾の横方向移動量, 直前の爆弾の縦方向移動量
    戻り値: 爆弾の縦方向移動量と横方向移動量のタプル
    こうかとんを追跡する爆弾の移動量を算出する関数
    """
    dist_x = kk_rct.center[0] - bb_rct.center[0] #  こうかとんと爆弾の横方向の距離を算出
    dist_y = kk_rct.center[1] - bb_rct.center[1] #  こうかとんと爆弾の縦方向の距離を算出
    origin_norm = abs(math.sqrt(math.pow(dist_x, 2) + math.pow(dist_y, 2))) #  ベクトルのノルムを算出

    if origin_norm < 300: #  ノルムが300未満の場合、直前の移動を継続
        return (vx, vy)
    
    norm_mag = math.sqrt(50) / origin_norm #  ノルムが√50となる倍率を計算
    return (dist_x * norm_mag, dist_y * norm_mag) #  倍率をかけて返却


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
