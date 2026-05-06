def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        bx, by = sx, sy
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = man(nx, ny, tx, ty) + 2 * man(nx, ny, ox, oy)
            if best is None or d < best:
                best = d
                bx, by = nx, ny
        return [bx - sx, by - sy]

    # Pick a target where we are relatively closer than opponent (intercept)
    best_t = None
    best_key = None
    for (rx, ry) in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (-(od - sd), sd, man(rx, ry, 0, 0) + man(rx, ry, gw - 1, gh - 1))
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    # Greedy 1-step lookahead with crowding: maximize relative advantage, also avoid moves that
    # leave us farther from the best target or let opponent get closer.
    tx, ty = best_t
    best_move = (0, 0)
    best_val = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        sd1 = man(nx, ny, tx, ty)
        od1 = man(ox, oy, tx, ty)
        # second-choice resource to avoid dead-ends
        sd2 = None
        for (rx, ry) in resources:
            if (rx, ry) == (tx, ty):
                continue
            d = man(nx, ny, rx, ry)
            if sd2 is None or d < sd2:
                sd2 = d
        if sd2 is None:
            sd2 = sd1 + 1
        val = (od1 - sd1) * 100 - sd1 * 3 - sd2
        # slight preference to keep moving (reduces stalling)
        if dx == 0 and dy == 0:
            val -= 5
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]