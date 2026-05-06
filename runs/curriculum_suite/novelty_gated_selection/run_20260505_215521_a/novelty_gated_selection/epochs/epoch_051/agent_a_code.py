def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if w <= 0 or h <= 0 or (sx, sy) in obst:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        tx, ty = 0, 0
        nx, ny = sx, sy
        if sx < ox: nx = sx + 1
        elif sx > ox: nx = sx - 1
        if sy < oy: ny = sy + 1
        elif sy > oy: ny = sy - 1
        if inb(nx, ny):
            return [nx - sx, ny - sy]
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    # Predict opponent's likely target: nearest resource to opponent.
    best_t = resources[0]
    best_dop = man((ox, oy), best_t)
    for r in resources[1:]:
        d = man((ox, oy), r)
        if d < best_dop:
            best_dop = d
            best_t = r

    # Also keep a secondary pull to nearest resource from us.
    best_us = resources[0]
    best_dus = man((sx, sy), best_us)
    for r in resources[1:]:
        d = man((sx, sy), r)
        if d < best_dus:
            best_dus = d
            best_us = r

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        us_to_t = man((nx, ny), best_t)
        op_to_t = best_dop  # opponent position unchanged this turn

        # Primary: try to become closer than opponent to their nearest target.
        score = (op_to_t - us_to_t) * 1000

        # Secondary: maintain progress toward our own nearest resource.
        score -= man((nx, ny), best_us) * 3

        # Tertiary: discourage drifting away from the map center to avoid getting stuck.
        cx, cy = w // 2, h // 2
        score -= (abs(nx - cx) + abs(ny - cy)) * 0.05

        # Slightly prefer reducing our distance to opponent (interception) when near.
        score += (10 - man((nx, ny), (ox, oy))) * 0.2

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move