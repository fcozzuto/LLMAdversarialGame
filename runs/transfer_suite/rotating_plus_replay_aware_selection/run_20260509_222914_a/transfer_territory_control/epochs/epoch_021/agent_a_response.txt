def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (7, 7)

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in observation.get("self_territory") or [])
    opp_terr = set(tuple(p) for p in observation.get("opponent_territory") or [])
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells") or [])

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    frontier = set()
    for x, y in self_terr:
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in self_terr:
                frontier.add((nx, ny))

    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def min_dist_to_set(p, S):
        if not S:
            return 99
        return min(man(p, q) for q in S)

    # Candidate evaluation favors: capturing unclaimed, catching opponent territory when adjacent,
    # expanding our frontier, and avoiding moving into opponent proximity.
    best = None
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # deterministic: engine would keep us in place

        pos = (nx, ny)
        if pos in self_terr:
            val = -0.3  # don't waste moves inside our area unless forced
        else:
            d_ours = min_dist_to_set(pos, self_terr) if self_terr else man(pos, (sx, sy))
            d_opp = min_dist_to_set(pos, opp_terr) if opp_terr else man(pos, (ox, oy))
            adj_frontier = 1.0 if pos in frontier else 0.0

            val = 0.0
            if pos in unclaimed:
                val += 6.0
            if pos in opp_terr:
                val += 8.0  # flipping gives strong immediate gain
            if pos in frontier:
                val += 2.5
            # prefer moving away from opponent unless we can flip them
            val += (3.5 - d_ours) * 0.8
            val += max(0, (d_opp - 1)) * 0.35
            if pos in opp_terr:
                val += max(0, (2 - d_opp)) * 1.2
        # tie-break deterministically toward smaller (dx,dy) in a fixed order
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]