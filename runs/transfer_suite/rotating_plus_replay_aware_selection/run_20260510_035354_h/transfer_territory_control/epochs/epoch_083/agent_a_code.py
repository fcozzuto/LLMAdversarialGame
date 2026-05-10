def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def toset(x):
        s = set()
        if not x:
            return s
        for p in x:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    opp_territory = toset(observation.get("opponent_territory"))
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    # Precompute resource positions (if any)
    res_pos = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res_pos.append((int(p[0]), int(p[1])))

    for dx, dy in moves:
        nx, ny = int(ax + dx), int(ay + dy)
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in opp_territory:
            score += 5000
        if (nx, ny) in unclaimed:
            score += 1200
        score += -abs(nx - ox) - abs(ny - oy)

        if res_pos:
            md = 10**9
            for rx, ry in res_pos:
                d = abs(nx - rx) + abs(ny - ry)
                if d < md:
                    md = d
            score += -md
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]