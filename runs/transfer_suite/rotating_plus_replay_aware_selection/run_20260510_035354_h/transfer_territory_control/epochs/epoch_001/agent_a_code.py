def choose_move(observation):
    ax, ay = observation.get("self_position", (0, 0))
    bx, by = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    obstacles = observation.get("obstacles", []) or []
    obs = set((x, y) for x, y in obstacles if 0 <= x < w and 0 <= y < h)

    uc = observation.get("unclaimed_cells", []) or []
    attack_mode = (observation.get("turn_index", 0) % 4) in (2, 3)

    target = (bx, by)
    if (not attack_mode) and uc:
        bestd = 10**9
        tx, ty = target
        for x, y in uc:
            if (x, y) in obs:
                continue
            d = abs(x - ax) + abs(y - ay)
            if d < bestd:
                bestd = d
                tx, ty = x, y
        target = (tx, ty)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    tx, ty = target
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        score = -d
        if (nx, ny) == (bx, by):
            score += 10**6
        if attack_mode:
            score += 1000 - d
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]