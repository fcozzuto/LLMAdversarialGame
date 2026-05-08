def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not candidates:
        return [0, 0]

    srole = str(observation.get("self_role", "")).lower()
    orole = str(observation.get("opponent_role", "")).lower()
    i_am_pursuer = (("pursuer" in srole) or ("chaser" in srole) or ("catch" in srole) or ("pursuit" in srole))
    if "evader" in srole or "evad" in srole:
        i_am_pursuer = False
    if (("pursuer" in orole) or ("chaser" in orole) or ("catch" in orole) or ("pursuit" in orole)):
        i_am_pursuer = False

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in dirs:
            if free(x + dx, y + dy):
                c += 1
        return c

    if i_am_pursuer:
        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            d = dist2(nx, ny, ox, oy)
            m = mobility(nx, ny)
            dx_next = nx - ox
            dy_next = ny - oy
            align = -(abs(dx_next) + abs(dy_next))  # prefer moving "through" gaps
            score = (-d, -m, align)  # minimize dist, then minimize loss of mobility, then prefer alignment
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]
    else:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target = max(corners, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy)) + (abs(c[0] - ox) + abs(c[1] - ox)))
        tx, ty = target
        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            d_opp = dist2(nx, ny, ox, oy)
            d_tgt = dist2(nx, ny, tx, ty)
            m = mobility(nx, ny)
            score = (d_opp, -d_tgt, m)  # maximize distance from pursuer, then move toward far corner, then keep mobility
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]