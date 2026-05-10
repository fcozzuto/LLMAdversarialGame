def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def diag_dist(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    resset = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                resset.append((x, y))
    if not resset:
        return [0, 0]

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                cand.append((dx, dy, nx, ny))
    if not cand:
        cand = [(0, 0, sx, sy)]

    best_move = None
    best_val = None
    grid_cx, grid_cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy, nx, ny in cand:
        # Greedy-but-deterministic: evaluate best target from the next position.
        best_target_val = None
        for rx, ry in resset:
            myd = diag_dist(nx, ny, rx, ry)
            oppd = diag_dist(ox, oy, rx, ry)
            # Primary: reach sooner than opponent.
            reach_margin = oppd - myd
            # Secondary: prefer closer targets when tieing, and slightly bias toward center.
            center_bias = -0.05 * (abs(rx - grid_cx) + abs(ry - grid_cy))
            # If opponent is also close, slightly increase urgency to deny.
            deny_bias = 0.1 * (1 if reach_margin > 0 else -1) * (1.0 / (1 + oppd))
            val = 2.0 * reach_margin - 0.2 * myd + center_bias + deny_bias
            if best_target_val is None or val > best_target_val or (val == best_target_val and (rx, ry) < best_target):
                best_target_val = val
                best_target = (rx, ry)
        if best_val is None or best_target_val > best_val or (best_target_val == best_val and (dx, dy) < best_move):
            best_val = best_target_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]