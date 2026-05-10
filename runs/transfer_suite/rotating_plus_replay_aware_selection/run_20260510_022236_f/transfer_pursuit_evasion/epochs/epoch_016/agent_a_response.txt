def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("evad" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    order = [m for m in moves if m != (0, 0)] + [(0, 0)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def free_neighbors_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    best_move = [0, 0]
    best_score = None

    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        neigh = free_neighbors_count(nx, ny)

        # Small deterministic tie-breaker: prefer moves that align with current relative direction.
        relx, rely = ox - sx, oy - sy
        align = (1 if dx == (1 if relx > 0 else (-1 if relx < 0 else 0)) else 0) + (1 if dy == (1 if rely > 0 else (-1 if rely < 0 else 0)) else 0)

        if pursuer:
            # Minimize distance to opponent; prefer higher mobility to avoid getting blocked.
            score = (-d, neigh, align, -abs(nx - ox) - abs(ny - oy))
        else:
            # Maximize distance to opponent; prefer higher mobility and slight movement away from opponent.
            score = (d, neigh, -align, abs(nx - ox) + abs(ny - oy))

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move