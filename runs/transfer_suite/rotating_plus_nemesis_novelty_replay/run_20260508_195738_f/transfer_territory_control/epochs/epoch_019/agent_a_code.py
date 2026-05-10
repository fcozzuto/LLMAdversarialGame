def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)
    opp_pos = observation.get("opponent_position", None)
    ox, oy = opp_pos if isinstance(opp_pos, (list, tuple)) and len(opp_pos) >= 2 else (x, y)
    oppT = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []) if p and len(p) >= 2)
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []) if p and len(p) >= 2)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 50
            for ddx, ddy in dirs:
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and (ax, ay) in oppT:
                    score += 120
        if (nx, ny) in oppT:
            score -= 80
        score -= abs(nx - ox) + abs(ny - oy)
        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return best