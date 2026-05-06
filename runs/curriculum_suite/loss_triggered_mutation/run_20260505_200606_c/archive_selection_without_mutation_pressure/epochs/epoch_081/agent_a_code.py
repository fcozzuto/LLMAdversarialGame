def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = p[0], p[1]
            if (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return None
        if (nx, ny) in obstacles:
            return None
        return (nx, ny)

    best = (0, 0)
    best_sc = -10**18
    # prioritize: immediate capture; then win resource contests; then closer to a good target; slight preference to move along best axis
    for dx, dy in moves:
        ns = legal(sx, sy, dx, dy)
        if ns is None:
            continue
        nx, ny = ns

        # if we land on a resource, take it decisively
        sc = 0
        immediate = 0
        for (rx, ry) in res:
            if rx == nx and ry == ny:
                immediate = 1
                break
        if immediate:
            sc += 10**6

        # evaluate best resource contest after this move
        best_delta = -10**18
        best_self_d = 10**9
        best_opp_d = 10**9
        for (rx, ry) in res:
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            delta = do - ds  # positive means we are closer
            # value: prefer being closer than opponent, then being very close
            val = delta * 1000 - ds
            if val > best_delta:
                best_delta = val
                best_self_d = ds
                best_opp_d = do

        # contest strength
        sc += best_delta
        # small tie-break: prefer reducing distance to the closest "contested" resource
        sc += max(0, (best_opp_d - best_self_d) * 10)
        # small tie-break: progress mostly in y (opponent edge_patrol tends to advance); deterministic via weighted sum
        sc += (ny - sy) * 3 + (nx - sx) * 1

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
        elif sc == best_sc:
            # deterministic tie-break: lexicographic on (dx,dy)
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]