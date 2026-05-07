def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = (-10**9, 10**9)  # (takeover, our_dist)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        takeover = do - ds  # prefer we arrive earlier
        # mild preference for closer resources to finish sooner
        key = (takeover, ds)
        if key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # Evaluate candidate moves; greedy toward target, avoid obstacles.
    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if inb(nx, ny):
                dist = cheb(nx, ny, tx, ty)
                # prefer progress toward target direction; break ties toward takeover
                dir_pref = 0
                if (mx, my) == (dx, dy):
                    dir_pref = 2
                elif (mx == dx or my == dy):
                    dir_pref = 1
                opp_dist = cheb(ox, oy, tx, ty)  # static, keeps deterministic
                takeover_now = opp_dist - dist
                candidates.append((dist - dir_pref, -takeover_now, mx, my))
    if not candidates:
        return [0, 0]
    candidates.sort()
    _, _, mx, my = candidates[0]
    return [int(mx), int(my)]