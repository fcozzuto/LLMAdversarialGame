def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # go toward opponent a bit to avoid deadlock
            s = abs(nx - ox) + abs(ny - oy)
            if s < best[0]:
                best = (s, dx, dy)
        return [best[1], best[2]]

    def man(a, b, x, y):
        return abs(x - a) + abs(y - b)

    best_score = -10**18
    best_move = (0, 0)
    # Deterministic tie-break: fixed move order, then dx,dy
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # If we can step onto a resource, strongly prefer it
        on_resource = 1 if (nx, ny) in set(resources) else 0

        # Choose best resource to chase where we gain over opponent
        best_local = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # diagonal allowed but Manhattan is a stable heuristic
            gain = do - ds  # positive means we're closer
            # also slightly prefer nearer resource to avoid wandering
            cand = gain * 100 - ds
            # tiny deterministic preference by coordinate
            cand += (-(rx + ry)) * 0.001
            if cand > best_local:
                best_local = cand

        # If opponent is extremely close to all resources, staying can be better
        opp_pressure = 0
        for rx, ry in resources:
            opp_pressure = max(opp_pressure, man(ox, oy, rx, ry) == 0 and 50 or 0)

        total = best_local + on_resource * 100000 - opp_pressure
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]