def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def dist(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        my_best_adv = None
        my_best_sd = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            myd = dist(sx, sy, rx, ry) if (nx == sx and ny == sy) else dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            adv = opd - myd  # want us closer than opponent
            sd = myd
            if (my_best_adv is None) or (adv > my_best_adv) or (adv == my_best_adv and sd < my_best_sd):
                my_best_adv, my_best_sd = adv, sd

        # secondary pressure: avoid moves that give opponent "free" access to same nearest resource
        # by penalizing being within 1 step of opponent relative to our best.
        penalty = 0
        if my_best_sd is not None:
            # nearest resource from opponent
            opp_sd = None
            for r in resources:
                rx, ry = int(r[0]), int(r[1])
                d = dist(ox, oy, rx, ry)
                if opp_sd is None or d < opp_sd:
                    opp_sd = d
            if opp_sd is not None and my_best_sd >= opp_sd:
                penalty = 1 if my_best_sd == opp_sd else 2

        val = (my_best_adv if my_best_adv is not None else -10, -penalty, -(my_best_sd if my_best_sd is not None else 10))
        if (best is None) or (val > best[0]):
            best = (val, [dx, dy])

    return best[1] if best is not None else [0, 0]