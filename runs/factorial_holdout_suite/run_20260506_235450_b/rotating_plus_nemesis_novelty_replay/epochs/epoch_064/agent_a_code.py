def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None
    res = []
    for r in resources:
        try:
            x, y = r
            res.append((x, y))
        except:
            pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        # No resources visible: drift toward center to reduce interception chances
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best, bestmv = -10**18, [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -(abs(nx - tx) + abs(ny - ty)) - (1 if dx == 0 and dy == 0 else 0)
            if sc > best:
                best, bestmv = sc, [dx, dy]
        return bestmv

    # Score moves by: (1) improve our reach to resources where we're closer than opponent,
    # (2) deny opponent by increasing their distance to that same resource.
    best, bestmv = -10**18, [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        best_gain = -10**18
        for rx, ry in res:
            d_self = abs(nx - rx) + abs(ny - ry)
            if opp_exists:
                d_opp = abs(ox - rx) + abs(oy - ry)
                # Prefer resources where we are closer (or become closer soon).
                # The denominator makes "winning a race" matter more than raw distance.
                race = (d_opp - d_self)  # positive is good
                sc = race * 3 - d_self
            else:
                sc = -d_self
            if sc > best_gain:
                best_gain = sc
        # Small bias to not just oscillate: prefer movement that reduces distance to the best resource race.
        sc_total = best_gain - (1 if dx == 0 and dy == 0 else 0)
        if sc_total > best:
            best, bestmv = sc_total, [dx, dy]
    return bestmv