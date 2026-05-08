def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Frontier preference: aim for unclaimed cells adjacent to opponent territory
    adj_frontier = set()
    for (x, y) in opp_t:
        for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                if (nx, ny) in unclaimed:
                    adj_frontier.add((nx, ny))

    # If no frontier, fall back to center / opponent direction
    prefer_frontier = len(adj_frontier) > 0 and observation.get("turn_index", 0) >= 3

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0.0
        if (x, y) in unclaimed:
            s += 3.2
        if (x, y) in opp_t:
            s += 6.0
        if (x, y) in self_t:
            s -= 0.2
        # Center pressure (helps build stable territory, reduces edge trapping)
        dcenter = abs(x - cx) + abs(y - cy)
        s += (2.0 - 0.25 * dcenter)
        # Opponent pressure / blocking
        if prefer_frontier:
            if (x, y) in adj_frontier:
                s += 7.0
            else:
                # small bias toward the closest frontier to reduce dithering
                if adj_frontier:
                    bf = min(adj_frontier, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
                    s += 1.5 - 0.18 * (abs(bf[0] - x) + abs(bf[1] - y))
        else:
            s += 0.9 - 0.15 * (abs(ox - x) + abs(oy - y))
        return s

    best = (sx, sy)
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = score_cell(nx, ny)
        if sc > best_s or (sc == best_s and (nx, ny) < best):
            best_s = sc
            best = (nx, ny)

    return [int(best[0] - sx), int(best[1] - sy)]