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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny):
                        yield nx, ny

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_val = -10**18
    best = (0, 0)

    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = ax, ay
            dx, dy = 0, 0
        val = 0.0

        if (nx, ny) in op_set:
            val += 120.0
        elif (nx, ny) in un_set:
            val += 60.0
        elif (nx, ny) in my_set:
            val += 5.0
        else:
            val += -5.0

        n = list(neigh8(nx, ny))
        op_adj = sum(1 for p in n if p in op_set)
        my_adj = sum(1 for p in n if p in my_set)
        un_adj = sum(1 for p in n if p in un_set)

        val += 15.0 * op_adj
        val += 8.0 * my_adj
        val += 5.0 * un_adj

        val += -0.8 * (abs(nx - ax) + abs(ny - ay))
        val += -0.1 * (abs(nx - cx) + abs(ny - cy))

        if val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]