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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose target: maximize our advantage = (opp_dist - my_dist), tie-break by smaller my_dist then coordinates.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        key = (-(adv), myd, ry, rx)  # convert to minimization
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Greedy step toward target with opponent avoidance and obstacle safety.
    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    scored = []
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Prefer reducing distance to target, while keeping away from opponent and not moving away from target too much.
        d_to = cheb(nx, ny, tx, ty)
        myd = cheb(nx, ny, ox, oy)
        # Primary: distance to target; Secondary: maximize distance from opponent; Tertiary: deterministic coordinate tie.
        score = (d_to, -myd, ny, nx)
        scored.append((score, dx, dy))
    if not scored:
        return [0, 0]
    scored.sort(key=lambda t: t[0])
    return [scored[0][1], scored[0][2]]