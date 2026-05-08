def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def to_set(v):
        s = set()
        if v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    s.add((int(p[0]), int(p[1])))
        return s

    self_set = to_set(observation.get("self_territory"))
    opp_set = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj(sset, x, y):
        for dx, dy in dirs:
            if (x + dx, y + dy) in sset:
                return True
        return False

    # Strategy: expand from our frontier to unclaimed; if close to opponent territory, step into it.
    # Tie-breaker: deterministic preference toward lower distance to board center and away from obstacles.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        score = 0
        if (nx, ny) in opp_set:
            score += 6
            if unclaimed:
                score += 2 if adj(self_set, nx, ny) else 0
            score += 1 if adj(opp_set, nx, ny) else 0
        elif (nx, ny) in unclaimed:
            score += 4
            score += 2 if adj(self_set, nx, ny) else -1
            score += 1 if adj(opp_set, nx, ny) else 0
        elif (nx, ny) in self_set:
            score += 1
            score += 1 if adj(self_set, nx, ny) else 0
        else:
            score += 0

        # Small shaping toward center to avoid stagnation
        dist_c = abs(nx - cx) + abs(ny - cy)
        score -= 0.05 * dist_c

        # Avoid getting boxed near obstacles
        neigh_blocked = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) in blocked:
                neigh_blocked += 1
        score -= 0.3 * neigh_blocked

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]