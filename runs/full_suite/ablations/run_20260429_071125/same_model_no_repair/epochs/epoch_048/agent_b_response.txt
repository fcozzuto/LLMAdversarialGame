def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Evaluate next move by best "capture pressure" over resources.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        move_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            du = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Pressure: we want to be closer than opponent and closer soon.
            # Big bonus for immediate/near capture, penalty when opponent already closer.
            v = (do - du) * 25
            if du == 0:
                v += 500
            elif du == 1:
                v += 120
            if do < du:
                v -= (du - do) * 60
            # Tie-break: prefer resources that are relatively closer to both (more likely to race).
            v -= (du + do) * 2
            if v > move_best:
                move_best = v

        # If we can't influence resources much, prefer moves that reduce distance to the best resource we currently target.
        if move_best < -10**17:
            move_best = -10**17 + cheb(nx, ny, sx, sy)

        if move_best > best_val:
            best_val = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]