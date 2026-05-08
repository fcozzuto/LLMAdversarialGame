def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    srole = (observation.get("self_role") or "").lower()
    orole = (observation.get("opponent_role") or "").lower()
    self_is_pursuer = ("purs" in srole) and ("evad" not in srole)
    if ("purs" not in srole) and ("purs" in orole):
        self_is_pursuer = False

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def mobility(x, y):
        c = 0
        for mx, my in moves:
            nx, ny = x + mx, y + my
            if inb(nx, ny):
                c += 1
        return c

    # Preferred "wall-running" target for evader: stay close to farthest corner relative to pursuer.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    wall_target = None
    if not self_is_pursuer:
        wall_target = max(corners, key=lambda c: dist(c[0], c[1], ox, oy))

    best = None  # (cmp1, cmp2, tie, dx, dy)
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue

        d = dist(nx, ny, ox, oy)
        mob = mobility(nx, ny)

        # Small deterministic tie-breakers to avoid oscillation preference near walls.
        wall_bias = 0
        if not self_is_pursuer:
            tx, ty = wall_target
            wall_bias = -dist(nx, ny, tx, ty)  # closer to target wall corner is better

        # cmp1: minimize for pursuer, maximize for evader
        if self_is_pursuer:
            cmp1 = d
            cmp2 = -mob
            tie = wall_bias
        else:
            cmp1 = -d
            cmp2 = -mob
            tie = wall_bias

        key = (cmp1, cmp2, tie, -nx, -ny, mx, my)
        if best is None or key < best[0]:
            best = (key, mx, my)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]