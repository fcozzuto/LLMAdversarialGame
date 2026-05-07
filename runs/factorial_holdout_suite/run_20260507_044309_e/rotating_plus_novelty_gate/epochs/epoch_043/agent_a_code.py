def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if resources:
        # If we can collect immediately, do it (deterministic, preferred).
        for rx, ry in resources:
            if rx == sx and ry == sy:
                return [0, 0]

        best = None
        best_score = -10**18
        best_tieb = 10**18

        # Each move: favor resources where we are closer than opponent; otherwise minimize our distance.
        for dx, dy, nx, ny in valid:
            local_best = -10**18
            local_tieb = 10**18
            for rx, ry in resources:
                my_d = mdist(nx, ny, rx, ry)
                op_d = mdist(ox, oy, rx, ry)
                adv = op_d - my_d  # positive means we are closer
                # Encourage immediate/near captures and being the exclusive closest mover.
                score = 10_000 * adv - 50 * my_d + 2 * op_d
                # Prefer taking resources that are not hopeless: higher adv, then lower my_d.
                if score > local_best or (score == local_best and (my_d < local_tieb)):
                    local_best = score
                    local_tieb = my_d

            # Small tie-break to reduce thrashing: prefer moves that also slightly increase adv to the best resource.
            if local_best > best_score:
                best_score = local_best
                best_tieb = local_tieb
                best = (dx, dy)
            elif local_best == best_score and local_tieb < best_tieb:
                best_tieb = local_tieb
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No resources visible: drift toward center deterministically, avoiding obstacles.
    tx, ty = w // 2, h // 2
    best = None; best_d = 10**18; best_i = 10**18
    for i, (dx, dy, nx, ny) in enumerate(valid):
        d = mdist(nx, ny, tx, ty)
        if d < best_d or (d == best_d and i < best_i):
            best_d = d; best_i = i; best = (dx, dy)
    return [int(best[0]), int(best[1])]