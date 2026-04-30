def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]
    if not resources:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target resource we can reach competitively (deterministic tie-break by coords)
    best_t = None
    best_val = None
    for rx, ry in sorted(resources):
        sd = d((sx, sy), (rx, ry))
        od = d((ox, oy), (rx, ry))
        val = (od - sd, -sd, -rx, -ry)  # prefer resources closer than opponent
        if best_val is None or val > best_val:
            best_val = val
            best_t = (rx, ry)

    rx, ry = best_t
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            sd_after = d((nx, ny), (rx, ry))
            # Small bias to reduce distance to opponent when we're not winning; helps occasional contesting
            od_now = d((ox, oy), (rx, ry))
            contest_bias = 0
            if sd_after > od_now:
                contest_bias = -d((nx, ny), (ox, oy)) * 0.001
            score = (-sd_after + contest_bias, -abs(dx) - abs(dy), dx, dy)
            cand.append((score, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]