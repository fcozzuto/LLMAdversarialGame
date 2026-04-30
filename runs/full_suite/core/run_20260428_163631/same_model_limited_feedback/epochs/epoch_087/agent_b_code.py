def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turn = int(observation.get("turn_index", 0))
    if not resources:
        moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            v = (abs(nx - ox) + abs(ny - oy)) - (abs(dx) + abs(dy))
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    danger = dist((sx, sy), (ox, oy)) <= 3
    parity_mode = (turn % 2 == 0)

    best_target = None
    best_key = None
    for r in resources:
        rt = tuple(r)
        if danger:
            # contest: head for a resource that is closer to us than to the opponent (or disrupt near them)
            k = (dist((sx, sy), rt) - dist((ox, oy), rt), dist((ox, oy), rt), -dist((sx, sy), rt))
        else:
            if parity_mode:
                # greedy nearest with a slight bias to keep away from opponent
                k = (dist((sx, sy), rt), -dist((ox, oy), rt))
            else:
                # switch: target a resource that increases separation while still being reachable
                k = (-dist((ox, oy), rt), dist((sx, sy), rt))
        if best_key is None or k < best_key:
            best_key, best_target = k, rt

    tx, ty = best_target
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        to_t = dist((nx, ny), (tx, ty))
        to_o = dist((nx, ny), (ox, oy))
        # If opponent is very close, prioritize moving away or blocking their approach deterministically
        val = 0
        if danger:
            val += 3.0 * to_o
            val += -2.0 * to_t
        else:
            val += -1.8 * to_t
            val += 0.7 * to_o
        # slight preference to reduce movement magnitude (deterministic tie-breaker)
        val += -0.01 * (abs(dx) + abs(dy))
        if val > best_val:
            best_val, best_move = val, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]