def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res = [tuple(p) for p in resources]
    best_move = [0, 0]
    best_val = -10**18

    # Deterministic tie-break: fixed iteration order of deltas, then lexicographic on (nx,ny).
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # For this candidate cell, assume optimal target among remaining resources.
        best_cell = -10**18
        for rx, ry in res:
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            advantage = opp_d - my_d  # positive => we are closer (or will be quicker)
            hit = 10000 if (nx, ny) == (rx, ry) else 0
            # Prefer taking resources immediately; otherwise pick high advantage and nearer targets.
            val = hit + advantage * 80 - my_d
            if val > best_cell:
                best_cell = val

        if best_cell > best_val:
            best_val = best_cell
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]