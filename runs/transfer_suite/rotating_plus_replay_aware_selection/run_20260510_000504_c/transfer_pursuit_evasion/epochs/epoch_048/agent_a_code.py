def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("hunter" in self_role)
    if not i_am_pursuer:
        if ("purs" in opp_role) or ("chase" in opp_role) or ("hunter" in opp_role):
            i_am_pursuer = False
        else:
            i_am_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def obstacle_penalty(nx, ny):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    p += 1
        return p

    def d2(nx, ny):
        dx = nx - ox
        dy = ny - oy
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx == ox and ny == oy) and not i_am_pursuer:
            continue  # avoid accidental capture when evading
        dist = d2(nx, ny)
        pen = obstacle_penalty(nx, ny)
        if i_am_pursuer:
            val = (dist, pen, abs(nx - sx) + abs(ny - sy), dx, dy)  # minimize dist
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            val = (-dist, pen, abs(nx - sx) + abs(ny - sy), dx, dy)  # maximize dist
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move