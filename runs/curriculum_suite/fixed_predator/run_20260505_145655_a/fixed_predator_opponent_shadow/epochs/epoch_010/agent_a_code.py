def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax + ay

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        for rx, ry in resources:
            st = man(nx, ny, rx, ry)
            ot = man(ox, oy, rx, ry)
            if nx == rx and ny == ry:
                val += 10**6
            elif st <= ot:
                val += 200 + (ot - st) * 25 - st
            else:
                val += -150 - (st - ot) * 18 - st

        # Pressure term: prefer moves that reduce distance to opponent slightly
        val += -(man(nx, ny, ox, oy))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]