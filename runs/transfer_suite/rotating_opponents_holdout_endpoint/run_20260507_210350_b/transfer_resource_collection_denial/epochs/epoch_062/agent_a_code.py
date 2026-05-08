def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Pick a resource where we are (significantly) closer than the opponent.
    best = None
    best_gain = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gain = do - ds
        key = (gain, -ds, -rx, -ry)
        if best is None or key > best_gain:
            best = (rx, ry)
            best_gain = key

    tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    # Move greedily toward target with deterministic obstacle-avoidance.
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [
        (desired_dx, desired_dy),
        (desired_dx, 0),
        (0, desired_dy),
        (desired_dx, -desired_dy),
        (-desired_dx, desired_dy),
        (0, 0),
        (1 if desired_dx >= 0 else -1, 1 if desired_dy >= 0 else -1),
        (-1 if desired_dx >= 0 else 1, -1 if desired_dy >= 0 else 1),
    ]

    best_step = (0, 0)
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        # Prefer reducing distance to target; if tied, keep/extend our advantage.
        val = (-nds, ndo - nds, -abs(nx - tx), -abs(ny - ty))
        if best_val is None or val > best_val:
            best_val = val
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]