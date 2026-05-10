def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "pursuit", "pursuer"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score(nx, ny):
        dman = abs(nx - ox) + abs(ny - oy)
        dche = max(abs(nx - ox), abs(ny - oy))
        dist_term = -dman if is_pursuer else dman
        dist_term2 = -dche if is_pursuer else dche
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obstacles:
                    adj += 1
        # Avoid stepping into obstacles or too close to them
        if (nx, ny) in obstacles:
            return -10**9 if is_pursuer else 10**9
        # Tiny deterministic tie-breaker: prefer lower dx, then lower dy
        return (dist_term * 100 + dist_term2 * 10) - adj * (50 if is_pursuer else 35)

    best = None
    best_pair = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Engine will keep in place if invalid/boundary/blocked; simulate by clamping
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx2, dy2 = 0, 0
        else:
            dx2, dy2 = dx, dy
        sc = score(nx, ny)
        pair = (sc, -abs(dx2), -abs(dy2), -dx2, -dy2)
        if best is None or pair > best_pair:
            best = (dx2, dy2)
            best_pair = pair

    return [int(best[0]), int(best[1])]