def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def count_adj_obst(x, y):
        c = 0
        for ddx, ddy in deltas:
            nx, ny = x + ddx, y + ddy
            if inb(nx, ny) and (nx, ny) in obs:
                c += 1
        return c

    def opp_greedy_next(px, py, tx, ty):
        bestd = None
        best = None
        for ddx, ddy in deltas:
            nx, ny = px + ddx, py + ddy
            if not inb(nx, ny) or (nx, ny) in obs:
                nx, ny = px, py
            d = cheb(nx, ny, tx, ty)
            if bestd is None or d < bestd or (d == bestd and (ddx, ddy) < best):
                bestd, best = d, (ddx, ddy)
        return best

    def target_corner():
        return (7, 7) if (sx, sy) != (7, 7) else (0, 0)

    if not resources:
        targets = [target_corner()]
    else:
        # deterministically keep a few promising targets
        scored = []
        for rx, ry in resources:
            scored.append((min(cheb(sx, sy, rx, ry), cheb(ox, oy, rx, ry)), cheb(sx, sy, rx, ry), rx, ry))
        scored.sort()
        targets = [(t[2], t[3]) for t in scored[:4]]

    best_move = (0, 0)
    best_val = None
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        adv_best = None
        for tx, ty in targets:
            d_self = cheb(nx, ny, tx, ty)
            opp_ddx, opp_ddy = opp_greedy_next(ox, oy, tx, ty)
            onx, ony = ox + opp_ddx, oy + opp_ddy
            if not inb(onx, ony) or (onx, ony) in obs:
                onx, ony = ox, oy
            d_opp = cheb(onx, ony, tx, ty)
            # higher is better: opponent farther than us after their greedy step
            adv = d_opp - d_self
            key = (adv, -count_adj_ob