def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    # Target: maximize being closer than opponent (oppd - selfd), then prefer closer to self
    best_t = None
    best_key = None
    for r in resources:
        sd = manh((sx, sy), r)
        od = manh((ox, oy), r)
        key = (od - sd, -sd)  # larger is better for first, then smaller sd
        if best_key is None or key > best_key:
            best_key = key
            best_t = r

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        after = manh((nx, ny), (tx, ty))
        # Encourage stepping toward target; add slight tie-breaker to avoid lingering
        linger_pen = 0 if (dx == 0 and dy == 0) else -0.05
        opp_after = manh((ox, oy), (tx, ty))
        score = after - (opp_after - after) * 0.1 + linger_pen
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]