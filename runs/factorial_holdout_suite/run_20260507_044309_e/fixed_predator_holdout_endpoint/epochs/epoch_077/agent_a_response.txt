def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy  # Chebyshev for diagonal turns

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # pick resource where we get temporal lead, and also where we're not too close to opponent's reach
    best = None
    for rx, ry in resources:
        self_d = dist((sx, sy), (rx, ry))
        opp_d = dist((ox, oy), (rx, ry))
        lead = opp_d - self_d
        # tie-break: prefer smaller opponent distance (more contested) when lead equal, then nearer resource to us
        key = (lead, -opp_d, -self_d, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    (tx, ty) = best[1]

    # choose move that advances to target while maximizing (lead) for the immediate step
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        new_self = dist((nx, ny), (tx, ty))
        new_lead = dist((ox, oy), (tx, ty)) - new_self

        # obstacle-avoidance: penalize stepping next to obstacle (but allow if necessary)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if 0 <= xx < w and 0 <= yy < h and (xx, yy) in obstacles:
                    adj_obs += 1

        # deterministic tie-break order
        key = (new_lead, -new_self, -adj_obs, -nx, -ny, -dx, -dy)
        if best_m is None or key > best_m[0]:
            best_m = (key, [dx, dy])

    return best_m[1] if best_m is not None else [0, 0]