def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not targets:
        best = None; bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            v = -man((nx, ny), (ox, oy))  # just keep away
            if bestv is None or v > bestv:
                bestv = v; best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # Choose next move maximizing advantage on the best resource (one-step lookahead).
    best = (0, 0); bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        self_to_nearest = None
        best_adv = -10**9
        for rx, ry in targets:
            sd = man((nx, ny), (rx, ry))
            od = man((ox, oy), (rx, ry))
            adv = od - sd  # positive means we are closer
            if self_to_nearest is None or sd < self_to_nearest:
                self_to_nearest = sd
            if adv > best_adv:
                best_adv = adv
        # Encourage taking a resource we are clearly closer to; otherwise reduce chase distance.
        v = best_adv * 20 - (self_to_nearest if self_to_nearest is not None else 0) - 2 * man((nx, ny), (ox, oy))
        if bestv is None or v > bestv:
            bestv = v; best = (dx, dy)
    return list(best)