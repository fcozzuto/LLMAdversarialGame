def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    def dist2(x, y):
        dx = x - cx
        dy = y - cy
        return dx * dx + dy * dy

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0.0
        if (x, y) in selfT:
            s += 1.5
        if (x, y) in uncla:
            s += 10.0 - 0.05 * dist2(x, y)
        if (x, y) in oppT:
            s += 28.0 - 0.02 * dist2(x, y)

        # Prefer moving toward contested frontier: cells adjacent to opponent territory
        adj_opp = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if inb(nx, ny) and (nx, ny) in oppT:
                    adj_opp += 1
        if adj_opp:
            s += 12.0 * adj_opp

        # Mild preference to center (territory leader bonus tends to reward stable control)
        s += 0.6 * (dist2(sx, sy) - dist2(x, y))

        return s

    # Primary: maximize immediate frontier/claim value
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = score_cell(nx, ny)

        # If we can step directly into opponent territory, prefer it strongly
        if (nx, ny) in oppT:
            val += 5.0

        if val > best[0]:
            best = (val, dx, dy)

    # If no move considered (edge case), stay
    return [best[1], best[2]]