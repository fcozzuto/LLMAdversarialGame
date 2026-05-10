def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation.get("opponent_position", (x, y))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))

    if not valid:
        return [0, 0]

    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if selfT:
        frontier = set()
        for tx, ty in selfT:
            for ddx, ddy in dirs8:
                nx, ny = tx + ddx, ty + ddy
                if (nx, ny) in unclaimed and (0 <= nx < w) and (0 <= ny < h) and (nx, ny) not in obstacles:
                    frontier.add((nx, ny))
        targets = list(frontier) if frontier else list(unclaimed)
    else:
        targets = list(unclaimed)

    # If we can take unclaimed, prioritize expanding from our frontier; otherwise push toward opponent.
    if targets:
        # Deterministic tie-break: closer, then lexicographically
        target = min(targets, key=lambda t: (cheb((x, y), t), t[0], t[1]))
    elif oppT:
        target = min(list(oppT), key=lambda t: (cheb((x, y), t), t[0], t[1]))
    else:
        target = (ox, oy)

    # Score candidate moves: prefer steps that reduce distance to target, and avoid stepping onto opponent territory unless necessary.
    opp_set = oppT
    best = None
    best_sc = None
    tdx, tdy = target
    for dx, dy in valid:
        nx, ny = x + dx, y + dy
        dist = cheb((nx, ny), (tdx, tdy))
        penalty = 0
        if (nx, ny) in opp_set:
            penalty = 2
        # Slight bias to move (not always stay) using deterministic turn-based weight
        sc = (-dist, penalty, abs(dx), abs(dy), nx, ny)
        if best is None or sc < best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]