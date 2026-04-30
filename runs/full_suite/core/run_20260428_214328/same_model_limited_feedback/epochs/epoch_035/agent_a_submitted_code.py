def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    def best_resource():
        best = None
        best_key = None
        for r in resources:
            if r in obstacles:
                continue
            rx, ry = r
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            # prefer resources where we are closer than opponent; break ties by position
            key = (od - sd, -sd, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = best_resource()
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        sd_after = dist(nx, ny, ox, oy)
        if target is not None and (nx, ny) == target:
            base = 100000
        else:
            base = 0
        self_t = dist(nx, ny, target[0], target[1]) if target is not None else 0
        opp_t = dist(ox, oy, target[0], target[1]) if target is not None else 0
        # reward moving closer to target and improving relative advantage
        score = base + (opp_t - self_t) * 10 + (-sd_after) + (-(abs(dx) + abs(dy)) * 0.01)
        key = (score, -abs(dx) - abs(dy), dx, dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]