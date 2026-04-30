def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd = dist((nx, ny), (nx, ny))
        # myd is 0; keep for completeness
        best_val = -10**18
        my_after = (nx, ny)
        for rx, ry in resources:
            my_d = dist(my_after, (rx, ry))
            op_d = dist((ox, oy), (rx, ry))
            # Prefer resources where we are closer than opponent; also prefer shorter my distance.
            val = (op_d - my_d) * 1000 - my_d
            if val > best_val:
                best_val = val
        score = best_val
        # Tie-breaker: prefer staying if score equal but otherwise deterministic by move order.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]