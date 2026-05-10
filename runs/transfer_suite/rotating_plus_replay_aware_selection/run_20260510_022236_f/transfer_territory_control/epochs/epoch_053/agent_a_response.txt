def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    my_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = -10**18

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    adj_op = {(ox + dx, oy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)}
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Prefer expansions and counter-sweeps; avoid moving into opponent immediate pressure.
        if (nx, ny) in unclaimed:
            val = 3000
        elif (nx, ny) in my_terr:
            val = 800
        elif (nx, ny) in op_terr:
            val = 900  # flipping is enabled; still avoid dying into their block
        else:
            val = 200  # stepping on neutral is ok if it improves position

        # Tactical distance shaping
        d_opp = man((nx, ny), (ox, oy))
        val += 35 * d_opp  # safer if we are farther from opponent

        # If we can flip, favor getting closer to opponent border
        if (nx, ny) in op_terr:
            val += 2600 / (1 + d_opp)

        # Territory advantage: encourage staying on our frontier when behind
        my_cnt = int(observation.get("self_territory_count") or len(my_terr))
        op_cnt = int(observation.get("opponent_territory_count") or len(op_terr))
        if my_cnt <= op_cnt:
            if (nx, ny) in my_terr:
                val += 250
            if (nx, ny) in unclaimed:
                val += 400

        # Center bias to reduce sweep vulnerability
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        val += 40 * (max(w, h) - dist_center)

        # Penalize stepping right next to opponent unless we are flipping/op has to chase
        if (nx, ny) in adj_op and (nx, ny) not in op_terr:
            val -= 1800 / (1 + man((nx, ny), (ox, oy)))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]