def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if len(p) >= 2)
    opp_pos = observation.get("opponent_position", None)
    if opp_pos is None:
        opp_pos = [w - 1, h - 1]
    ox, oy = opp_pos

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def neigh_count(x, y, S):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in S:
                    c += 1
        return c

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        gain = 0
        if (nx, ny) in unclaimed:
            gain += 4.5
        if (nx, ny) in oppT:
            gain += 6.0
        if (nx, ny) in selfT:
            gain += 0.8

        # Prefer center and avoid edges (opponent is edge-claimer).
        dist_center = abs(nx - cx) + abs(ny - cy)
        gain += -0.12 * dist_center
        gain += 0.10 * edge_dist(nx, ny)

        # Reduce exposure near opponent territory; also step toward/away deterministically.
        gain -= 0.35 * (neigh_count(nx, ny, oppT))
        gain -= 0.06 * (abs(nx - ox) + abs(ny - oy))

        # Gentle cohesion: prefer cells adjacent to our territory.
        gain += 0.15 * neigh_count(nx, ny, selfT)

        if gain > best_val:
            best_val = gain
            best = (dx, dy)
    return [int(best[0]), int(best[1])]