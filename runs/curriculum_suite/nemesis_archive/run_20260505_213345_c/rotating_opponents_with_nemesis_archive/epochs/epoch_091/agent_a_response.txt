def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist8(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev (diagonal-friendly)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Opponent archetype: nearest_resource (Manhattan-ish). Use Chebyshev for our movement consistency.
    opp_best = min(resources, key=lambda r: dist8((ox, oy), r))
    opp_best_d = dist8((ox, oy), opp_best)

    best = (-(10**9), 0, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        my_best_d = min(dist8((nx, ny), r) for r in resources)
        # Advantage: get closer to the nearest remaining resource than opponent is to theirs,
        # plus a bonus for specifically contesting opponent's nearest resource.
        contest_d = dist8((nx, ny), opp_best)
        adv = (opp_best_d - my_best_d) + 0.8 * (opp_best_d - contest_d)

        # Small preference to progress vs staying and avoid oscillation without using history:
        # favor lower distance to centroid of resources (deterministic shaping).
        cx_sum = 0
        cy_sum = 0
        for r in resources:
            cx_sum += r[0]
            cy_sum += r[1]
        cx = cx_sum // len(resources)
        cy = cy_sum // len(resources)
        shape = -dist8((nx, ny), (cx, cy))

        # Deterministic tie-break: lexicographic on move
        cand = (adv + 0.05 * shape, -my_best_d, (dx, dy))
        if cand > best:
            best = cand

    return [best[2][0], best[2][1]]