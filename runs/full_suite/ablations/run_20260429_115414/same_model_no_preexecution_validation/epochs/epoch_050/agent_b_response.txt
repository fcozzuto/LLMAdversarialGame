def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    bestv = -10**18
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        gain = do - ds  # positive: we are closer (or can tie/deny)
        center_bias = -((tx - (w - 1) / 2.0) ** 2 + (ty - (h - 1) / 2.0) ** 2)
        # If we are farther, still sometimes contest near-ties; penalize strongly when do >> ds is negative.
        v = 200 * gain + 0.2 * center_bias - 0.01 * (ds + do)
        if v > bestv or (v == bestv and (tx, ty) < best):
            bestv = v
            best = (tx, ty)

    tx, ty = best
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opts = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dnew = cheb(nx, ny, tx, ty)
        # tie-break deterministically: prefer not moving away from opponent denial (increase do - ds)
        gain_new = cheb(ox, oy, tx, ty) - dnew
        opts.append((dnew, -gain_new, dx, dy))
    if not opts:
        return [0, 0]
    opts.sort()
    return [int(opts[0][2]), int(opts[0][3])]