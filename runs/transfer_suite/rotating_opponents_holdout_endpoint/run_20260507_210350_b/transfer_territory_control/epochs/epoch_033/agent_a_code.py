def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        if not v:
            return s
        for p in v:
            if p is None:
                continue
            try:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
            except Exception:
                pass
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    opp_terr = to_set(observation.get("opponent_territory"))
    self_terr = to_set(observation.get("self_territory"))

    best = (0, 0)
    best_score = -10**9

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Higher is better
        score = 0
        score += 60 if (nx, ny) in unclaimed else 0
        score -= 40 if (nx, ny) in opp_terr else 0
        score += 20 if (nx, ny) in self_terr else 0

        dist_opp = abs(nx - ox) + abs(ny - oy)
        score += 6 * dist_opp  # keep away

        # Prefer moving toward board center slightly
        dist_center = abs(nx - cx) + abs(ny - cy)
        score -= 0.5 * dist_center

        # Deterministic tie-break: prefer non-diagonal and then lexicographic dx,dy
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]