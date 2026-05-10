def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    turn = observation.get("turn_index", 0)
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles if 0 <= x < w and 0 <= y < h)
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    my_set = set((x, y) for x, y in my_t if 0 <= x < w and 0 <= y < h)
    op_set = set((x, y) for x, y in op_t if 0 <= x < w and 0 <= y < h)
    unclaimed = observation.get("unclaimed_cells") or []
    un = set((x, y) for x, y in unclaimed if 0 <= x < w and 0 <= y < h)
    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    frontier = set()
    for x, y in my_set:
        for nx, ny in neighbors8(x, y):
            if (nx, ny) in un:
                frontier.add((nx, ny))
    targets = list(frontier)
    if not targets:
        targets = list(un)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def best_target():
        if not targets:
            return None
        # slight deterministic oscillation to vary tie-breaks
        k = (turn % 4)
        def key(t):
            x, y = t
            d = abs(x - ax) + abs(y - ay)
            dc = abs(x - cx) + abs(y - cy)
            bias = (x + 2*y + k) % 3
            return (d, dc, bias, y, x)
        return min(targets, key=key)

    tgt = best_target()

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = 0
        if (nx, ny) in un:
            val += 120
        if (nx, ny) in op_set:
            val += 90
        # prefer moving toward a chosen target
        if tgt is not None:
            tx, ty = tgt
            val += 60 - (abs(tx - nx) + abs(ty - ny)) * 2
        # prefer approaching opponent territory to enable flips
        if op_set:
            md_op = min(abs(ox - nx) + abs(oy - ny) for ox, oy in op_set)
            val += 30 - md_op
        # stay slightly away from obstacles
        if obs:
            md_ob = min(abs(ox - nx) + abs(oy - ny) for ox, oy in obs)
            val += 2 * (md_ob == 1)  # discourage stepping adjacent if possible
        # tie-break deterministically: center then lexicographic
        val += -0.01 * (abs(nx - cx) + abs(ny - cy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]