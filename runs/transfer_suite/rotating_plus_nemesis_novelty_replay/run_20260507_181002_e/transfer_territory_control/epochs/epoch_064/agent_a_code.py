def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    if not unclaimed:
        resources = toset(observation.get("resources"))
        if resources:
            unclaimed = set(resources)

    if not unclaimed:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def boundary_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    # Strategy: grab unclaimed cells that are close to us, far from opponent, and not on the boundary
    best = None
    best_val = -10**18
    for tx, ty in unclaimed:
        if (tx, ty) in obstacles:
            continue
        d_us = md(sx, sy, tx, ty)
        d_op = md(ox, oy, tx, ty)
        if d_us == 0:
            val = 1e9
        else:
            # Prefer deeper (interior) claims to counter edge-claimer; also deny opponent by favoring larger d_op.
            interior = boundary_dist(tx, ty)
            center = -(abs(tx - cx) + abs(ty - cy))
            # Mild preference for reducing our distance quickly
            val = (2.5 * d_op) - (3.0 * d_us) + (0.9 * interior) + (0.35 * center)
        if val > best_val:
            best_val = val
            best = (tx, ty)

    tx, ty = best
    dx = clamp(tx - sx, -1, 1)
    dy = clamp(ty - sy, -1, 1)

    # Safety: if the immediate target is an obstacle, pick the best alternative among legal deltas toward same target.
    nxt = (sx + dx, sy + dy)
    if nxt in obstacles:
        cand = []
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                # steer toward the same tx,ty; also keep away from opponent
                cand.append((-(md(nx, ny, tx, ty)) + 0.2 * md(nx, ny, ox, oy), mx, my))
        if cand:
            cand.sort(reverse=True)
            return [int(cand[0][1]), int(cand[0][2])]
        return [0, 0]

    return [int(dx), int(dy)]