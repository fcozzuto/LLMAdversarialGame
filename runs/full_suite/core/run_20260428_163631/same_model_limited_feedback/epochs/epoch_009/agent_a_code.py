def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if dx == 0 and dy == 0:
                    continue
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    d = (nx - ox) ** 2 + (ny - oy) ** 2
                    if d > bestv:
                        bestv = d
                        best = [dx, dy]
        return best
    def d2(a, b):
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])
    # Score resources by my arrival advantage; also bias away from those too close to opponent.
    best_r = resources[0]
    best_score = 10**18
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        my = d2((sx, sy), (rx, ry))
        op = d2((ox, oy), (rx, ry))
        score = my - 1.15 * op
        # Tie-break: prefer closer overall to me
        score += 0.03 * my
        if score < best_score:
            best_score = score
            best_r = r
    tx, ty = best_r
    # Greedy move among legal deltas; if equal, prefer moves that reduce opponent threat to target.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    best = [0, 0]
    bestv = -10**18
    for dx, dy, nx, ny in candidates:
        my_to = d2((nx, ny), (tx, ty))
        op_to = d2((ox, oy), (tx, ty))
        # Higher is better: minimize my distance, maximize relative advantage.
        v = -my_to + 0.35 * (op_to - my_to)
        # Slightly encourage moving rather than staying when not at target
        if dx == 0 and dy == 0:
            v -= 0.15
        # If at/near target, prefer staying
        if my_to == 0:
            v += 2.0
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best