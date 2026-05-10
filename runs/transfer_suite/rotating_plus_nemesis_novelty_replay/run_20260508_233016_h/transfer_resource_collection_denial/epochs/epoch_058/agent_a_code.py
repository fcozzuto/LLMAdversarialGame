def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    best_t = None
    best_key = None
    for rx, ry in resources:
        d_my = dist(sx, sy, rx, ry)
        d_op = dist(ox, oy, rx, ry)
        secure = d_my < d_op
        # Prefer secure earliest; otherwise prefer denying most (op closer than us).
        key = (0 if secure else 1, d_my if secure else -(d_op - d_my), d_op - d_my, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_to_target = dist(nx, ny, tx, ty)
        d_to_opp = dist(nx, ny, ox, oy)

        # If stepping onto a resource, strongly prefer.
        on_res = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0

        # Deny: if opponent is closer to some resource, we try to approach the most contested one.
        denom = 0
        mind = 10**9
        for rx, ry in resources:
            dm = dist(nx, ny, rx, ry)
            dop = dist(ox, oy, rx, ry)
            if dop <= dm:  # we're not earlier; potentially contested/denied
                gain = dop - dm
                if gain > 0:
                    denom = max(denom, gain)
            mind = min(mind, dm)
        # Score combines: progress to target, avoid letting opponent reach sooner, and contest pressure.
        score = (on_res * 10_000) + (-(d_to_target * 10)) + (-(min(d_to_opp, 6))) + (denom * 2) + (-(mind))
        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]