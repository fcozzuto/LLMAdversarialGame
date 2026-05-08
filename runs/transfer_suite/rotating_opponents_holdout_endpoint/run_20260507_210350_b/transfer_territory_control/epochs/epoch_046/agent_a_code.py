def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def to_set(lst):
        s = set()
        for p in (lst or []):
            if p and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    self_terr = to_set(observation.get("self_territory"))
    opp_terr = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    opp_pos = observation.get("opponent_position") or [None, None]
    ox = int(opp_pos[0]) if opp_pos[0] is not None else None
    oy = int(opp_pos[1]) if opp_pos[1] is not None else None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**15
        else:
            if (nx, ny) in self_terr:
                val = 0.6
            elif (nx, ny) in unclaimed:
                val = 3.2 + 0.20 * edge_dist(nx, ny)
            elif (nx, ny) in opp_terr:
                val = 2.8 + 0.15 * edge_dist(nx, ny) + 0.35
            else:
                val = 1.0  # should be rare
            if ox is not None and oy is not None:
                val -= 0.08 * manh(sx, sy, ox, oy)
                val += 0.05 * manh(nx, ny, ox, oy)
            val += 0.02 * (edge_dist(nx, ny) - edge_dist(sx, sy))
        if val > best_val:
            best_val = val
            best = [dx, dy]
        elif val == best_val and best is not None:
            if (dx, dy) < (best[0], best[1]):
                best = [dx, dy]
    return best if best is not None else [0, 0]