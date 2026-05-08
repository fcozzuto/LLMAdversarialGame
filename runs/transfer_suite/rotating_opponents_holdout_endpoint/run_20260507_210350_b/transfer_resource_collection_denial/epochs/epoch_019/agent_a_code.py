def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If any resource can be taken immediately, do it.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in obstacles:
            continue
        if inb(nx, ny) and (nx, ny) in set(resources):
            return [dx, dy]

    rset = set(resources)
    best = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Score the best resource from this candidate position.
        cand = -10**18
        for tx, ty in rset:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            # Prefer resources where we're closer than opponent; also prefer nearer overall.
            advantage = od - sd
            tie = (tx * 131 + ty * 67 + sd * 7 + od * 3) % 1000
            v = advantage * 20 - sd + (1 if sd == 0 else 0) * 10000 + tie * 1e-6

            # Safety: if opponent is about to grab the same resource (within 1 step), don't chase it.
            if od <= 1 and sd > 1 and advantage < 0:
                v -= 40

            if v > cand:
                cand = v

        # Mild preference for reducing distance to nearest resource to avoid dithering.
        nearest_sd = min(man(nx, ny, tx, ty) for (tx, ty) in rset)
        cand += -nearest_sd * 0.2

        if cand > bestv:
            bestv = cand
            best = (dx, dy)

    return [int(best[0]), int(best[1])]