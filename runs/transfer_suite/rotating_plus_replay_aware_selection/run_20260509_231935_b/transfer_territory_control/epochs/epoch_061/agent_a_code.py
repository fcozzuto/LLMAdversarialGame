def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)]
    best = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 50
        if (nx, ny) in self_terr:
            score += 5
        if (nx, ny) in opp_terr:
            score += 80
        # Prefer moving away from opponent when safe, else move toward unclaimed/opp territory
        md = abs(nx - ox) + abs(ny - oy)
        score += (30 - md)
        # Slightly prefer positions closer to center for stability
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= abs(nx - cx) + abs(ny - cy)
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best