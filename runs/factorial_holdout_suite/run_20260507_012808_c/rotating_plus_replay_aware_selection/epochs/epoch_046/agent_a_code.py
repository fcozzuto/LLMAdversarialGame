def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def mdist(x1, y1, x2, y2):
        return abs(x2 - x1) + abs(y2 - y1)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for ddx, ddy in dirs:
            nx, ny = sx + ddx, sy + ddy
            if valid(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    best_score = -10**18
    best_move = (0, 0)

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        best_adv = -10**18
        for rx, ry in resources:
            my_d = mdist(nx, ny, rx, ry)
            op_d = mdist(ox, oy, rx, ry)
            adv = (op_d - my_d) * 1000 - my_d
            best_adv = adv if adv > best_adv else best_adv
        # Prefer capturing likely next turn: when we land on a resource, adv will be huge.
        score = best_adv
        if score > best_score:
            best_score = score
            best_move = (ddx, ddy)

    return [best_move[0], best_move[1]]