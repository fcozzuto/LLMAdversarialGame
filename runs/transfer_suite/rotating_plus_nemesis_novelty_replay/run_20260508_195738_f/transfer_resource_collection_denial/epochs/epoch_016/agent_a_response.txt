def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(x), int(y)) for x, y in obstacles_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Primary: go to a resource that maximizes "tempo" advantage over opponent.
    best_move = (0, 0)
    best_val = -10**12
    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Evaluate best target for this immediate move
            local_best = -10**12
            for rx, ry in resources:
                rx, ry = int(rx), int(ry)
                self_d = abs(nx - rx) + abs(ny - ry)
                opp_d = abs(ox - rx) + abs(oy - ry)
                # Prefer moves that reduce our remaining distance relative to opponent, then break ties by closer self_d.
                val = (opp_d - self_d) * 10 + (-self_d)
                if val > local_best:
                    local_best = val
            if local_best > best_val:
                best_val = local_best
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Fallback: deterministic cornering pressure.
    tx = 0 if ox > sx else (w - 1 if ox < sx else sx)
    ty = 0 if oy > sy else (h - 1 if oy < sy else sy)
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [int(dx), int(dy)]

    # If corner move blocked, take any valid step that reduces Manhattan distance to (tx, ty).
    cur_best = 10**12
    cur_move = (0, 0)
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        d = abs(tx - nx) + abs(ty - ny)
        if d < cur_best:
            cur_best = d
            cur_move = (mdx, mdy)
    return [int(cur_move[0]), int(cur_move[1])]