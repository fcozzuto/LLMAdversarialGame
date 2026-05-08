def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_t = set(tuple(p[:2]) for p in (observation.get("self_territory", []) or []) if p and len(p) >= 2)
    opp_t = set(tuple(p[:2]) for p in (observation.get("opponent_territory", []) or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p[:2]) for p in (observation.get("unclaimed_cells", []) or []) if p and len(p) >= 2)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cell_priority(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in opp_t:
            base = 70.0
        elif (x, y) in unclaimed:
            base = 25.0
        elif (x, y) in self_t:
            base = 8.0
        else:
            base = 12.0
        # Go toward opponent; slightly discourage moving away.
        dist_now = abs(ox - sx) + abs(oy - sy)
        dist_new = abs(ox - x) + abs(oy - y)
        base += 6.0 * (dist_now - dist_new)
        # Small preference to keep near unclaimed frontier and avoid dead-ends.
        neigh_open = 0
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                neigh_open += 1
        base += 0.3 * neigh_open
        return base

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            sc = -10**9
        else:
            sc = cell_priority(nx, ny)
        # Deterministic tie-break: prefer higher dx, then higher dy, then earlier dirs order.
        cand = (sc, dx, dy)
        if cand[0] > best[0] or (cand[0] == best[0] and (cand[1], cand[2]) > (best[1], best[2])):
            best = cand

    return [int(best[1]), int(best[2])]