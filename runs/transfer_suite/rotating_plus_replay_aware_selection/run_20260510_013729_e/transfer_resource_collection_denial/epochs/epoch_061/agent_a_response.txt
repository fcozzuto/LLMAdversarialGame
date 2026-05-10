def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = c - a
        if dx < 0:
            dx = -dx
        dy = d - b
        if dy < 0:
            dy = -dy
        return dx + dy

    # Order matters for deterministic tie-breaking
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            val = -10**12
        else:
            cur_best = -10**18
            for rx, ry in sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1])):
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                lead = do - ds  # positive if we are closer than opponent
                cap = 6.0 if (nx, ny) == (rx, ry) else 0.0
                # Encourage moving toward nearer targets but keep strong denial pressure
                val_target = cap + 1.25 * lead - 0.15 * ds
                if val_target > cur_best:
                    cur_best = val_target
            # Slightly prefer staying mobile: shorter self->opponent straightness
            val = cur_best - 0.01 * man(nx, ny, ox, oy)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]