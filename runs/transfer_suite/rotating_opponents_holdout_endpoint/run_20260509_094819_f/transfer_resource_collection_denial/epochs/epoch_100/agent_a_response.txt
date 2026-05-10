def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
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
        return dx if dx >= dy else dy

    # Prefer resources we can beat the opponent on (ds < do), then shortest ds.
    best = None
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # Small deterministic tie-break using coordinates and resource parity.
        key = (-(do - ds), -ds, -((x + y) & 1), -x, -y)
        if best is None or key < best[0]:
            best = (key, x, y)
    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    primary = (sx + dx, sy + dy)
    candidates.append(primary)
    candidates.append((sx + dx, sy))
    candidates.append((sx, sy + dy))
    candidates.append((sx, sy))
    # Deterministic obstacle avoidance: try other axis order and orthogonal alternatives.
    candidates.append((sx + (-dx if dx != 0 else 0), sy + dy))
    candidates.append((sx + dx, sy + (-dy if dy != 0 else 0)))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    for nx, ny in candidates:
        if valid(nx, ny):
            return [nx - sx, ny - sy]

    return [0, 0]