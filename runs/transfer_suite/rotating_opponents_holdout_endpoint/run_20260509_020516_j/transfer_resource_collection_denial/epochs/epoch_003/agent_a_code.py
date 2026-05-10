def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    env = observation.get("environment_name", "resource_collection")

    if env != "resource_collection" or not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        best_key = (10**9, 10**9, 10**9)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    continue
                d = abs(tx - nx) + abs(ty - ny)
                key = (d, abs(dx) + abs(dy), dx * dx + dy * dy)
                if key < best_key:
                    best_key = key
                    best = [dx, dy]
        return best

    def nearest_d(px, py, rx, ry):
        return abs(rx - px) + abs(ry - py)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer staying legal and moving toward the resource we are most advantaged for.
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate by best target after the move.
        # advantage: opponent distance - self distance (higher is better)
        # tie-break: collect closer first.
        local_best = (-10**9, 10**9, 10**9, 0)
        for rx, ry in resources:
            sd = nearest_d(nx, ny, rx, ry)
            od = nearest_d(ox, oy, rx, ry)
            adv = od - sd
            # If we'd land on the resource, strongly favor.
            land = 1 if (nx == rx and ny == ry) else 0
            key = (adv, -land, sd, abs(rx - ox) + abs(ry - oy))
            if key > local_best:
                local_best = key

        # Incorporate move preference: avoid oscillation by favoring progress toward resources overall.
        # Use sum of distances to closest k=2 resources as a proxy (deterministic).
        dists = sorted(nearest_d(nx, ny, rx, ry) for rx, ry in resources)
        proxy = dists[0] + (dists[1] if len(dists) > 1 else dists[0])
        move_mag = abs(dx) + abs(dy)

        score_tuple = (local_best[0], local_best[1], -local_best[2], -local_best[3], -move_mag, -proxy)
        if best_score is None or score_tuple > best_score:
            best_score = score_tuple
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]