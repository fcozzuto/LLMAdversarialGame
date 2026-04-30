def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def is_valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        # Choose a resource we are likely to reach first; otherwise pick the least contested.
        scored = []
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            contested = 5 if od < sd else 0
            # slight preference away from opponent to reduce gifting
            lead_margin = od - sd
            risk = 0 if lead_margin <= 0 else 2  # if we're closer, mildly penalize far resources to finish
            val = sd + contested + risk
            scored.append((val, sd, od, rx, ry))
        scored.sort()
        _, _, _, tx, ty = scored[0]
    else:
        tx, ty = ox, oy  # drift; no resources visible

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not is_valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # Primary: minimize distance to target; Secondary: avoid being closer to opponent; Tertiary: deterministic tie-break
        key = (d_to_t, -d_to_o, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]