def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def pick_target():
        if not resources:
            return (w - 1, h - 1)
        best = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources I can reach sooner; if tie, prefer farther from opponent
            key = (opd - myd, -opd, -myd, rx, ry)
            if best is None or key > best[0]:
                best = (key, rx, ry)
        return (best[1], best[2])

    tx, ty = pick_target()

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # If immediate target is blocked, retarget to closest available neighbor direction
    if not inb(tx, ty):
        # choose an unblocked resource if any, else nearest unblocked corner
        for rx, ry in sorted([(int(x), int(y)) for x, y in resources], key=lambda p: cheb(sx, sy, p[0], p[1])):
            if inb(rx, ry):
                tx, ty = rx, ry
                break
        else:
            for gx, gy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
                if inb(gx, gy):
                    tx, ty = gx, gy
                    break

    best_dxdy = (0, 0)
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        # Also bias to reduce opponent reach to same target
        oppd_to_target = cheb(ox, oy, tx, ty)
        myd_now = cheb(sx, sy, tx, ty)
        my_adv = (oppd_to_target - (myd)) - (oppd_to_target - myd_now)
        key = (-myd, -opd, my_adv, -cheb(nx, ny, tx, ty), nx, ny)
        if best is None or key > best:
            best = key
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]