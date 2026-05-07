def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            oxp, oyp = int(o[0]), int(o[1])
            if 0 <= oxp < w and 0 <= oyp < h:
                obstacles.add((oxp, oyp))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target: maximize winning likelihood against opponent.
    # Score = (opp_dist - self_dist) - 0.01*self_dist - 1e-6*(rx+ry) for deterministic tie-break.
    best = None
    best_score = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        sc = (do - ds) - 0.01 * ds - 1e-6 * (rx + ry)
        if sc > best_score:
            best_score = sc
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # Prefer move that reduces our distance; avoid obstacles; deterministic neighbor ordering.
    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                continue
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                # primary: closer to target, secondary: also closer than opponent, tertiary: deterministic.
                ns = cheb(nx, ny, rx, ry)
                no = cheb(ox, oy, rx, ry)
                rel = (no - ns)
                candidates.append((ns, -rel, (mx, my)))
    candidates.sort(key=lambda t: (t[0], t[1], t[2][0], t[2][1]))

    # First choice: best candidate; if none, try stepping in direct diagonal/axis direction ignoring rel.
    if candidates:
        return [int(candidates[0][2][0]), int(candidates[0][2][1])]

    # Fallback: try direct direction(s) that are legal.
    direct = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for mx, my in direct:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mx), int(my)]

    return [0, 0]