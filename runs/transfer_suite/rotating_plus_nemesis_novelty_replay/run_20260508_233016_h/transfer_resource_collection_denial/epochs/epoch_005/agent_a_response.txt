def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    res_set = set(tuple(r) for r in resources)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Immediate safe capture
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in res_set and (nx, ny) not in obstacles:
            return [dx, dy]

    # One-step lookahead: maximize best relative advantage to any resource
    def best_for_pos(px, py):
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = dist2(px, py, rx, ry)
            od = dist2(ox, oy, rx, ry)
            if sd == 0:
                rel = 10**9
            else:
                rel = (od - sd)
            # Prefer being closer and also creating distance from opponent
            val = (rel, -sd, -(abs(rx - px) + abs(ry - py)), -(abs(rx - ox) + abs(ry - oy)))
            if best is None or val > best:
                best = val
        return best if best is not None else (0, 0, 0, 0)

    best_move = (None, None)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        v = best_for_pos(nx, ny)
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]