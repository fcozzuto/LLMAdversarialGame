def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    opp_pos = observation.get("opponent_position", None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def neigh_cnt(x, y, S):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in S:
                    c += 1
        return c

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        base = 0
        if (nx, ny) in unclaimed:
            base += 10
        if (nx, ny) in oppT:
            base += 7  # flip on entry
        if (nx, ny) in selfT:
            base += 2
        # Create expansion opportunities and favor safer center-ish territory vs edge-grab
        base += 0.9 * neigh_cnt(nx, ny, unclaimed)
        base -= 0.18 * edge_dist(nx, ny)
        # If we can take near-opponent territory quickly, do it; otherwise avoid moving toward their fringe
        if opp_pos and len(opp_pos) == 2:
            od = abs(nx - opp_pos[0]) + abs(ny - opp_pos[1])
            sd = abs(sx - opp_pos[0]) + abs(sy - opp_pos[1])
            base += 0.12 * (sd - od)
        # Prefer continuing forward into unclaimed rather than oscillating
        base += 0.02 * (nx + ny)
        if base > best[0] or (base == best[0] and (dx, dy) < (best[1], best[2])):
            best = (base, dx, dy)

    dx, dy = best[1], best[2]
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]