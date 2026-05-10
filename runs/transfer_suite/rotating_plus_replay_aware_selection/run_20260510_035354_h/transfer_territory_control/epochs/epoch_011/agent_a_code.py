def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    turn = observation.get("turn_index", 0)
    obstacles = observation.get("obstacles") or []
    obs = {(x, y) for x, y in obstacles if 0 <= x < w and 0 <= y < h}
    unclaimed = observation.get("unclaimed_cells") or []
    un = {(x, y) for x, y in unclaimed if 0 <= x < w and 0 <= y < h}
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    my_set = {(x, y) for x, y in my_t if 0 <= x < w and 0 <= y < h}
    op_set = {(x, y) for x, y in op_t if 0 <= x < w and 0 <= y < h}

    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    target_un = None
    if un:
        bestd = 10**9
        for ux, uy in un:
            d = abs(ux - ax) + abs(uy - ay)
            if d < bestd or (d == bestd and (ux, uy) < target_un):
                bestd = d
                target_un = (ux, uy)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        if (nx, ny) in un:
            val += 1200
        if (nx, ny) in op_set:
            val += 650  # flipping is enabled
        if (nx, ny) in my_set:
            val += 80

        my_adj_un = 0
        my_adj_op = 0
        my_adj_my = 0
        for tx, ty in neighbors8(nx, ny):
            if (tx, ty) in un: my_adj_un += 1
            if (tx, ty) in op_set: my_adj_op += 1
            if (tx, ty) in my_set: my_adj_my += 1

        val += my_adj_un * 35
        val += my_adj_op * 22
        val -= my_adj_my * 6

        dist_center = abs(nx - center_x) + abs(ny - center_y)
        val -= dist_center * (0.8 if (turn % 8) in (0, 1) else 0.35)

        if target_un is not None:
            tx, ty = target_un
            val -= (abs(nx - tx) + abs(ny - ty)) * (7.0 if (turn % 5) != 4 else 3.0)

        if (dx, dy) < best_move:
            pass
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]