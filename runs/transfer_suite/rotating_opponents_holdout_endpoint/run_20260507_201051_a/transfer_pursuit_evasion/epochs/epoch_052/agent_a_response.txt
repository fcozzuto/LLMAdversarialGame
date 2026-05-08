def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obs_adj(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obs:
                    c += 1
        return c

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        # Prefer moving to/through obstacle-dense funnels when evading, and
        # prefer approaching while avoiding being surrounded when pursuing.
        adj = obs_adj(nx, ny)
        if "pursuer" in role:
            # Aggressive chase: minimize distance; slightly prefer safer positions.
            val = (d, adj)
            if best_val is None or (val[0] < best_val[0]) or (val[0] == best_val[0] and val[1] < best_val[1]):
                best_val = val
                best = (dx, dy)
        else:
            # Evade: maximize distance; if tie, head toward farthest corner and avoid being adjacent to obstacles.
            far_corner = max(corners, key=lambda c: dist2(nx, ny, c[0], c[1]))
            corner_score = dist2(far_corner[0], far_corner[1], ox, oy)
            val = (-d, corner_score, -adj)
            if best_val is None:
                best_val = val
                best = (dx, dy)
            else:
                better = (val[0] < best_val[0]) or (val[0] == best_val[0] and (val[1] > best_val[1] or (val[1] == best_val[1] and val[2] > best_val[2])))
                if better:
                    best_val = val
                    best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]