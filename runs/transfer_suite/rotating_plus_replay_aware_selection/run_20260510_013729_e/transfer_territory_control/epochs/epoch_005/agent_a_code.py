def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(a, b): return 0 <= a < w and 0 <= b < h

    def adj_cells(p):
        px, py = p
        out = []
        for dx, dy in dirs:
            if dx == 0 and dy == 0: 
                continue
            nx, ny = px + dx, py + dy
            if inb(nx, ny):
                out.append((nx, ny))
        return out

    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def score_cell(c):
        if c in obs:
            return -10**9
        if c in self_ter:
            return 2
        if c in unclaimed:
            # Prefer getting near opponent boundary
            d_to_opp = dist(c, (ox, oy))
            # Also prefer cells near opponent territory
            adj_opp = sum(1 for nb in adj_cells(c) if nb in opp_ter)
            return 6 + 0.6 * adj_opp - 0.05 * d_to_opp
        if c in opp_ter:
            # Prefer capturing opponent territory that is near their border
            adj_self = sum(1 for nb in adj_cells(c) if nb in self_ter)
            adj_opp = sum(1 for nb in adj_cells(c) if nb in opp_ter)
            return 10 + 0.4 * adj_self + 0.2 * adj_opp
        return 0

    # Build a deterministic set of goals: unclaimed adjacent to opponent territory, else nearest unclaimed, else drift toward opponent
    border = []
    for c in unclaimed:
        if any(nb in opp_ter for nb in adj_cells(c)):
            border.append(c)
    if border:
        border.sort(key=lambda c: (dist(c, (x, y)), dist(c, (ox, oy)), c[0], c[1]))
        goals = border[:6]
    else:
        uc = list(unclaimed)
        if uc:
            uc.sort(key=lambda c: (dist(c, (x, y)), c[0], c[1]))
            goals = uc[:6]
        else:
            goals = [(ox, oy)]

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        c = (nx, ny)
        if c in obs:
            continue
        immediate = score_cell(c)
        # Distance to best goal (deterministic tie-break)
        dg = min(dist(c, g) for g in goals)
        # Also mildly prefer moving to reduce distance to opponent when contesting
        d_opp_now = dist((x, y), (ox, oy))
        d_opp_next = dist(c, (ox, oy))
        chase = (d_opp_now - d_opp_next)
        total = immediate * 10 - dg + 0.8 * chase
        if total > best[0] or (total == best[0] and (dx, dy) < (best[1], best[2])):
            best = (total, dx, dy)

    return [int(best[1]), int(best[2])]