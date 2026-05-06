def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If we can stay on a resource, do it.
    if (sx, sy) in resources:
        return [0, 0]

    # Race heuristic: maximize (opponent lead reduction) toward the best contestable resource.
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # If landing on a resource, prioritize immediately.
        if (nx, ny) in resources:
            return [dx, dy]

        my = (nx, ny)
        # Deterministically choose the most favorable resource to race for.
        # Higher value is better: smaller my_dist, larger opponent_dist.
        best_res_val = -10**9
        best_res = None
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                continue
            d1 = dist(my, (rx, ry))
            d2 = dist((ox, oy), (rx, ry))
            # Encourage getting there sooner than opponent; break ties lexicographically.
            val = (d2 - d1) * 10 - d1
            if val > best_res_val or (val == best_res_val and (rx, ry) < best_res):
                best_res_val = val
                best_res = (rx, ry)

        # Also lightly penalize moving away from overall resource mass.
        # Use a simple proxy: min dist to any resource.
        min_my = min(dist(my, r) for r in resources)
        val2 = best_res_val - min_my
        if val2 > best_val:
            best_val = val2
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]