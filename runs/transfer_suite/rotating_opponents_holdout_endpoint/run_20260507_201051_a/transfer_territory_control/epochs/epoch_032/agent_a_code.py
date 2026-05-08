def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = (observation.get("self_position") or [0, 0])[:2]
    oxp, oyp = (observation.get("opponent_position") or [w - 1, h - 1])[:2]

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))
    st = set(map(tuple, observation.get("self_territory") or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Deterministic bias: prefer moves that progress toward an opponent frontier target.
    if unclaimed:
        frontier_points = list(unclaimed)
        # pick a deterministic "frontier centroid": closest unclaimed to opponent territory if available
        if ot:
            t = min(frontier_points, key=lambda p: abs(p[0] - sum(x for x, _ in ot) / len(ot)) + abs(p[1] - sum(y for _, y in ot) / len(ot)))
            tx, ty = t
        else:
            t = min(frontier_points, key=lambda p: abs(p[0] - oxp) + abs(p[1] - oyp))
            tx, ty = t
    elif ot:
        tx = sum(x for x, _ in ot) / len(ot)
        ty = sum(y for _, y in ot) / len(ot)
    else:
        tx, ty = oxp, oyp

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        # Heuristic rewards
        reward = 0
        if cell in ot:
            reward += 220  # flipping opponent territory is strong
        elif cell in unclaimed:
            reward += 120  # taking unclaimed grows your control
        elif cell in st:
            reward += 15   # maintaining territory is fine

        # Prefer approaching target/frontier
        dist = abs(nx - tx) + abs(ny - ty)
        reward += -2.5 * dist

        # Avoid moving away from opponent when no unclaimed exist
        if not unclaimed and ot:
            reward += -1.2 * (abs(nx - oxp) + abs(ny - oyp))

        # Tiny tie-breakers for determinism: favor x then y increasing
        reward += -0.01 * nx - 0.001 * ny

        if reward > best_score:
            best_score = reward
            best_move = [dx, dy]

    return best_move