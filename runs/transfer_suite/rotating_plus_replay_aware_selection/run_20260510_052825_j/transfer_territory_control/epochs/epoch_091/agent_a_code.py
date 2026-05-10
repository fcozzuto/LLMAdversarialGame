def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    opp_pos = observation.get("opponent_position", None)
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def edge_bonus(x, y):
        d = min(x, w - 1 - x, y, h - 1 - y)
        return (w + h - 2 * d) * 0.08

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_opp_dist(x, y):
        if opp_pos and len(opp_pos) == 2:
            return abs(x - opp_pos[0]) + abs(y - opp_pos[1])
        if oppT:
            bx = 10**9
            for ox, oy in oppT:
                d = abs(x - ox) + abs(y - oy)
                if d < bx:
                    bx = d
            return bx
        return 10**6

    def nearest_self_dist(x, y):
        if selfT:
            bx = 10**9
            for ux, uy in selfT:
                d = abs(x - ux) + abs(y - uy)
                if d < bx:
                    bx = d
            return bx
        return 0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    behind = observation.get("self_territory_count", 0) <= observation.get("opponent_territory_count", 0)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0.0
        if (nx, ny) in unclaimed:
            score += 18.0
        if (nx, ny) in oppT:
            score += 12.0
        if (nx, ny) in selfT:
            score += 3.0

        score += edge_bonus(nx, ny)

        # Create/maintain a compact frontier; avoid splitting by moving away too far from self.
        score -= max(0, nearest_self_dist(nx, ny) - 2) * 0.6

        od = nearest_opp_dist(nx, ny)
        if behind:
            score += 10.0 / (1.0 + od)  # counter-claim pressure
        else:
            score += (od * 0.08)  # keep distance while expanding

        # Light deterministic pattern to break ties
        score += ((observation.get("turn_index", 0) + nx * 3 + ny * 5) % 7) * 0.01

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]