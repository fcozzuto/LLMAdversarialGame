def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Select target resource based on who can reach first
    best = None
    for dx, dy, nx, ny in valid:
        if (nx, ny) in obstacles:
            continue
        if not resources:
            # No resources: move away from opponent and toward center deterministically
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score = (dist((nx, ny), (ox, oy)) * 10) - (abs(nx - cx) + abs(ny - cy))
        else:
            # Evaluate each resource; prefer moves that reduce my lead over opponent
            score = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                my_d = dist((nx, ny), (rx, ry))
                opp_d = dist((ox, oy), (rx, ry))
                # Lower is better: be closer than opponent
                s = (my_d - opp_d) * 100 + my_d
                if (rx + ry) % 2 == 0:
                    s += 1  # deterministic tie breaker
                if score is None or s < score:
                    score = s
            # If can capture immediately, strongly prioritize
            if (nx, ny) in set(tuple(r) for r in resources):
                score -= 10_000
        if best is None or score < best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]