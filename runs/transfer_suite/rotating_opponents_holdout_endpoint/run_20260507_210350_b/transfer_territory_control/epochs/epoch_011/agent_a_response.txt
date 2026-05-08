def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    def to_set(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    self_t = to_set(observation.get("self_territory"))
    opp_t = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    resources = to_set(observation.get("resources"))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # "Center" bias to avoid getting stuck in corners
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def neigh_block_count(x, y):
        c = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + ddx, y + ddy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                c += 1
        return c

    best = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0

        if (nx, ny) in unclaimed:
            score += 120
        if (nx, ny) in opp_t:
            score += 85  # flipping is enabled on entry
        if (nx, ny) in self_t:
            score += 10

        if (nx, ny) in resources:
            score += 20

        # Prevent obstacle hugging
        score -= 6 * neigh_block_count(nx, ny)

        # Move toward center slightly when no immediate gains
        distc = abs(nx - cx) + abs(ny - cy)
        score -= 0.8 * distc

        # Prefer reducing opponent control where possible (crude: choose moves adjacent to opponent territory)
        adj_opp = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ax, ay = nx + ddx, ny + ddy
            if (ax, ay) in opp_t:
                adj_opp += 1
        score += 7 * adj_opp

        # Deterministic tie-break: fixed order via dirs iteration
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best