def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    env = observation.get("environment_name", "resource_collection")

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if env != "resource_collection" or not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        best_key = (10**9, 10**9, 10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d = abs(tx - nx) + abs(ty - ny)
            key = (d, abs(dx) + abs(dy), dx * dx + dy * dy)
            if key < best_key:
                best_key = key
                best = [dx, dy]
        return best

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        local_best = 10**9
        for rx, ry in resources:
            d_self = manhattan(nx, ny, rx, ry)
            d_opp = manhattan(ox, oy, rx, ry)
            if d_self == 0:
                score = -10000
            else:
                margin = d_opp - d_self  # positive means we're closer
                score = (1.6 * d_self) - (0.6 * d_opp) - (2.0 * margin / 8.0)
                if margin < 0:
                    score += 5.0  # deprioritize contested/denied resources
            if score < local_best:
                local_best = score

        if best_score is None or local_best < best_score or (local_best == best_score and [dx, dy] < best_move):
            best_score = local_best
            best_move = [dx, dy]

    return best_move if best_score is not None else [0, 0]