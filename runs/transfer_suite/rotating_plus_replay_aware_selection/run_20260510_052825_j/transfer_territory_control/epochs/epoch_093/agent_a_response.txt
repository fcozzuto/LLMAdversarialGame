def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    ox, oy = observation.get("opponent_position", (sx, sy))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ed(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def best_opp_dist(x, y):
        if not oppT:
            return abs(x - ox) + abs(y - oy)
        # sample a few closest-ish points deterministically
        pts = list(oppT)
        pts.sort(key=lambda p: (abs(p[0] - x) + abs(p[1] - y), abs(p[0] - ox) + abs(p[1] - oy)))
        k = 4 if len(pts) > 4 else len(pts)
        d = 10**9
        for i in range(k):
            px, py = pts[i]
            dd = abs(px - x) + abs(py - y)
            if dd < d:
                d = dd
        return d if d < 10**9 else abs(x - ox) + abs(y - oy)

    best = (-(10**18), (0, 0))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in oppT:
            # entering opponent territory is risky vs sweeper; flip may happen but we still avoid if possible
            score = -50 - best_opp_dist(nx, ny) * 2
        elif (nx, ny) in selfT:
            score = 1 + 0.03 * (w + h - 2 * ed(nx, ny))
        elif (nx, ny) in unclaimed:
            score = 80 + 0.10 * (w + h - 2 * ed(nx, ny))
        else:
            score = 2 + 0.03 * (w + h - 2 * ed(nx, ny))
        # push toward farthest-from-opponent unclaimed: territory_sweeper tends to chase; we counter-raid edges
        d_opp = best_opp_dist(nx, ny)
        score += 0.6 * d_opp
        # discourage wasting steps into center
        score += 0.02 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        # prefer slight progress away from opponent position
        score += 0.04 * (abs(sx - ox) + abs(sy - oy) - (abs(nx - ox) + abs(ny - oy)))
        # tiny tie-breaker toward staying consistent
        score += 1e-6 * (dx * 0 + dy * 0)
        if score > best[0]:
            best = (score, (dx, dy))

    return [int(best[1][0]), int(best[1][1])]