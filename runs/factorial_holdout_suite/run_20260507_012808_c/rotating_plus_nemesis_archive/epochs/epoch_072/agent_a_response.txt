def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    # If no visible resources, drift to center with obstacle-avoidance and slight anti-cornering.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            score = abs(nx - tx) + abs(ny - ty)
            if (best is None) or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Choose move that improves our race advantage on the best contested resource.
    # Advantage: (opponent distance - self distance). Prefer higher advantage.
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        local_best = None
        for r in resources:
            ds_now = man((nx, ny), r)
            do_now = man((ox, oy), r)
            adv = do_now - ds_now
            # If we can step onto a resource, strongly prefer it.
            if (nx, ny) == r:
                adv += 1000
            # Tie-break deterministically: closer resources first, then lexicographic.
            aux = (adv, -ds_now, -(r[0] * 100 + r[1]))
            if (local_best is None) or aux > local_best[0]:
                local_best = (aux, r)
        # Also consider avoiding moving away from all resources slightly.
        overall = local_best[0][0]
        if (best_score is None) or (overall > best_score) or (overall == best_score and (dx, dy) < best_move):
            best_score = overall
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]