def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    best_r = None
    best_key = None
    for r in resources:
        if not r or len(r) != 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inside(rx, ry):
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer or tied; otherwise penalize.
        closer_bad = 0 if myd <= opd else 1
        key = (closer_bad, myd, -opd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_r

    valid = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    best_move = None
    best_move_key = None
    for dx, dy, nx, ny in valid:
        myd2 = cheb(nx, ny, tx, ty)
        # Advantage: being closer than opponent to the chosen target is good.
        opd2 = cheb(ox, oy, tx, ty)
        myd_curr = cheb(sx, sy, tx, ty)
        # Also encourage reducing my distance to target immediately.
        dist_improve = myd_curr - myd2
        key = (
            myd2,                      # go towards target (smaller better)
            0 if myd2 <= opd2 else 1,  # prefer positions not worse than opponent
            -dist_improve,             # maximize improvement
            abs((nx - tx)) + abs((ny - ty)),  # mild tie-break
            dx, dy
        )
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]