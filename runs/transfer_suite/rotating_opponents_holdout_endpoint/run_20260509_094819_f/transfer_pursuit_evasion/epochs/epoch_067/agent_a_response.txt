def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = (observation.get("self_role") or "").lower()
    self_is_pursuer = "pursuer" in role

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    edge_dist = lambda x, y: min(x, y, w - 1 - x, h - 1 - y)

    def score(nx, ny):
        dx = abs(nx - ox)
        dy = abs(ny - oy)
        d = dx + dy
        # obstacle handling: avoid moving adjacent to obstacles (evader) / use open paths (pursuer)
        adj_obs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if abs(ddx) + abs(ddy) == 0:
                    continue
                if (nx + ddx, ny + ddy) in blocked:
                    adj_obs += 1
        cmin = min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
        if self_is_pursuer:
            # chase with slight corner pressure; prefer moves that increase "freedom" from obstacles
            return -d - 0.25 * edge_dist(nx, ny) + 0.2 * cmin + 0.6 * adj_obs
        else:
            # evade: maximize distance; also prefer edges (often harder to chase) but not dead-adjacent to obstacles
            return d + 0.15 * edge_dist(nx, ny) - 0.75 * adj_obs + 0.05 * cmin

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = score(nx, ny)
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None:
        # all blocked (rare): stay
        return [0, 0]
    return best