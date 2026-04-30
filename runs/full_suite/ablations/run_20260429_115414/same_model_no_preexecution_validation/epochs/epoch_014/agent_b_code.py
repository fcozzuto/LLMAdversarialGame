def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def legal(x, y): return inb(x, y) and (x, y) not in obs_set

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick target with a different emphasis than pure distance: prefer "race wins" and penalize ties.
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if sd == 0: score = 10**9  # already on it (rare)
        else:
            lead = od - sd
            # If tied or opponent is close, prefer farther lead and relative positioning away from board center.
            center_bias = -((rx - w // 2) * (rx - w // 2) + (ry - h // 2) * (ry - h // 2))
            tie_pen = -200 if od == sd else 0
            score = lead * 50 + (-sd) * 5 + center_bias + tie_pen
        key = (score, -sd, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    # One-step look: avoid moves that let the opponent capture/become no-worse immediately.
    opp_can = False
    self_dist_now = cheb(sx, sy, tx, ty)
    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if not legal(nx, ny):
            continue
        if nx == tx and ny == ty:
            opp_can = True
            break
    # Evaluate our best move.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer moving closer, also prefer increasing separation from opponent when race is risky.
        sep = cheb(nx, ny, ox, oy)
        val = -nd * 20 + sep * 1.5

        # Opponent response estimate: is there an opponent move that makes them <= us on the target next?
        risky = 0
        my_next = nd
        opp_next_best = 10**9
        for odx, ody in dirs:
            anx, any = ox + odx, oy + ody
            if not legal(anx, any):
                continue
            opp_next_best = min(opp_next_best, cheb(anx, any, tx, ty))
        if opp_next_best <= my_next:
            risky = 80 if opp_next_best == 0 else 40
        val -= risky

        # Small preference to keep our own distance advantage if possible.
        if self_dist_now > 0: