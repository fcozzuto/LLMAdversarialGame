def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    best = [0, 0]
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        closest_lose = 10**9
        for rx, ry in resources:
            selfd = abs(nx - rx) + abs(ny - ry)
            oppd = abs(ox - rx) + abs(oy - ry)

            # Win pressure for resources we can reach before opponent (or tie).
            margin = oppd - selfd
            if margin >= 0:
                sc += 18 * margin - 2 * selfd
            else:
                closest_lose = min(closest_lose, -margin)
                sc -= 10 * (-margin) + selfd

            # Encourage moving toward at least one resource quickly.
            sc += -0.15 * selfd

        # If we're losing everywhere, reduce speed toward the "least lost" resource.
        sc -= 0.5 * closest_lose

        # Tiny tie-breaker: prefer staying away from opponent if equally good.
        sc -= 0.02 * (abs(nx - ox) + abs(ny - oy))

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best