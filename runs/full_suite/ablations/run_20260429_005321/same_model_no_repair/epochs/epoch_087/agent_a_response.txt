def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal_moves(x, y):
        out = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                out.append((dx, dy, nx, ny))
        if not out:
            return [(0, 0, x, y)]
        return out

    legal = legal_moves(sx, sy)
    if not resources:
        tx = 0 if sx > (w - 1) // 2 else w - 1
        ty = 0 if sy > (h - 1) // 2 else h - 1
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, tx, ty)
            score = -d
            if best is None or (score > best[0]) or (score == best[0] and (dx, dy) == (0, 0) and best[1] != (0, 0)):
                best = (score, dx, dy)
        return [best[1], best[2]]

    best_overall = None
    for dx, dy, nx, ny in legal:
        my_to_opp = cheb(nx, ny, ox, oy)
        # Score by best resource advantage (opp closer => bad; I closer => good)
        best_adv = None
        best_my = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d  # positive means I am closer than opponent at their current pos
            if best_adv is None or adv > best_adv or (adv == best_adv and my_d < best_my):
                best_adv = adv
                best_my = my_d
        # Encourage securing resources; fallback reduces distance to opponent and closest resource slightly.
        score = best_adv * 1000 - best_my - my_to_opp * 0.05
        if best_overall is None or score > best_overall[0] or (score == best_overall[0] and (dx, dy) == (0, 0)):
            best_overall = (score, dx, dy)
    return [best_overall[1], best_overall[2]]