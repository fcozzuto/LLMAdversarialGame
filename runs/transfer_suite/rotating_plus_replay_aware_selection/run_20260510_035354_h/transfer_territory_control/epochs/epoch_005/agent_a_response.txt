def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    turn = observation.get("turn_index", 0)

    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles if 0 <= x < w and 0 <= y < h)

    unclaimed = observation.get("unclaimed_cells") or []
    un = set((x, y) for x, y in unclaimed if 0 <= x < w and 0 <= y < h)

    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    my_set = set((x, y) for x, y in my_t if 0 <= x < w and 0 <= y < h)
    op_set = set((x, y) for x, y in op_t if 0 <= x < w and 0 <= y < h)

    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    my_adj_op = set()
    for x, y in my_set:
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in op_set:
                my_adj_op.add((x, y))
                break

    center = (w - 1) / 2.0, (h - 1) / 2.0
    bias_op = (turn % 6) in (3, 4)

    def dist_to_center(x, y):
        cx, cy = center
        return abs(x - cx) + abs(y - cy)

    best = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        if (nx, ny) in op_set:
            val += 220  # direct capture pressure (flip enabled on entry)
            if (ax, ay) in my_adj_op:
                val += 30
        if (nx, ny) in un:
            val += 120  # expand into neutral space

        # Frontier control: prefer moves that increase adjacent unclaimed and reduce adjacent opponent.
        adj_un = 0
        adj_op = 0
        adj_my = 0
        for ddx, ddy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
            tx, ty = nx + ddx, ny + ddy
            if not inb(tx, ty):
                continue
            if (tx, ty) in un:
                adj_un += 1
            if (tx, ty) in op_set:
                adj_op += 1
            if (tx, ty) in my_set:
                adj_my += 1

        val += 18 * adj_un
        val -= 28 * adj_op
        val += 6 * adj_my

        # Slight tie-break: go for edges/targets depending on bias_op
        val += (6 if bias_op else 0) * (nx in (0, w-1) or ny in (0, h-1))
        val -= 1.5 * dist_to_center(nx, ny)

        # Deterministic preference for staying only if truly not improving
        if dx == 0 and dy == 0:
            val -= 2

        # Deterministic tie-break by dir order implicitly via strict >
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]