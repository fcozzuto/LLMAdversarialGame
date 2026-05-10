def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []

    my_set = {(x, y) for x, y in my_t if 0 <= x < w and 0 <= y < h}
    op_set = {(x, y) for x, y in op_t if 0 <= x < w and 0 <= y < h}
    un_set = {(x, y) for x, y in unclaimed if 0 <= x < w and 0 <= y < h}
    obs_set = {(x, y) for x, y in obstacles if 0 <= x < w and 0 <= y < h}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny):
                        yield nx, ny

    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
    opp_front_un = []
    for ux, uy in un_set:
        for nx, ny in neigh8(ux, uy):
            if (nx, ny) in op_set:
                opp_front_un.append((ux, uy))
                break
    targets = opp_front_un if opp_front_un else list(un_set)
    if not targets:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = -10**18
    best_move = (0, 0)

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            nx, ny = ax, ay
        if (nx, ny) in obs_set:
            nx, ny = ax, ay
            dx, dy = 0, 0

        gain = 0
        if (nx, ny) in op_set:
            gain += 120
        elif (nx, ny) in un_set:
            gain += 70
        elif (nx, ny) in my_set:
            gain += 10

        td = 10**9
        for tx, ty in targets:
            d = manh(nx, ny, tx, ty)
            if d < td:
                td = d
        dist_center = abs(nx - center_x) + abs(ny - center_y)
        val = gain - td - 0.02 * dist_center

        if val > best or (val == best and (dx, dy) < best_move):
            best, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]