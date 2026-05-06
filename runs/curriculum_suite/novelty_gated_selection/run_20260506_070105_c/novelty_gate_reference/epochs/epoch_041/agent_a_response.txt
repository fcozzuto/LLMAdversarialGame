def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer resources where we can arrive first (intercept ahead of opponent).
    best = None
    best_adv = -10**9
    best_dself = 10**9
    for (rx, ry) in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = (od - sd) * 100 - sd  # strongly favor advantage; tie-break by speed
        if adv > best_adv or (adv == best_adv and sd < best_dself):
            best_adv = adv
            best_dself = sd
            best = (rx, ry)

    tx, ty = best

    def step_towards(t):
        rx, ry = t
        dx = 0 if rx == sx else (1 if rx > sx else -1)
        dy = 0 if ry == sy else (1 if ry > sy else -1)
        return dx, dy

    dx, dy = step_towards((tx, ty))
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        # Deterministic obstacle avoidance: try axis steps first, then diagonal-less.
        candidates = []
        if dx != 0: candidates.append((dx, 0))
        if dy != 0: candidates.append((0, dy))
        candidates.append((dx, dy))
        candidates.append((0, 0))
        for cdx, cdy in candidates:
            nnx, nny = sx + cdx, sy + cdy
            if 0 <= nnx < w and 0 <= nny < h and (nnx, nny) not in obstacles:
                return [int(cdx), int(cdy)]
        return [0, 0]

    return [int(dx), int(dy)]