def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target selection: prefer resources we can claim strictly earlier; otherwise minimize our time
    best = None
    best_key = None
    for i, r in enumerate(resources):
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not inb(rx, ry):
            continue
        st = cheb(sx, sy, rx, ry)
        ot = cheb(ox, oy, rx, ry)
        ahead = ot - st
        # Primary: maximize advantage; Secondary: smaller st; Tertiary: deterministic index
        key = (0 if ahead <= 0 else 1, ahead, -st, -i)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    # Local step: move closer to target with obstacle avoidance; deterministic tie-break by move order
    best_step = (0, 0)
    best_dist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if best_dist is None or d < best_dist or (d == best_dist and (dx, dy) == (0, 0)):
            best_dist = d
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]