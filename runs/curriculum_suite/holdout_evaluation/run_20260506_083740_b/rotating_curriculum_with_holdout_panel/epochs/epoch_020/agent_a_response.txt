def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx = 0 if sx > w - 1 - sx else w - 1
        ty = 0 if sy > h - 1 - sy else h - 1
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        # fallback: pick any valid move
        for mdx, mdy in moves:
            nx, ny = sx + mdx, sy + mdy
            if valid(nx, ny):
                return [mdx, mdy]
        return [0, 0]

    # Prefer moves that make us closer to some resource than opponent, while avoiding dead-ends.
    best_score = -10**18
    best_move = [0, 0]
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue

        # obstacle/corner pressure: fewer invalid neighbor moves is worse
        dead = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if not valid(ax, ay):
                dead += 1

        move_score = -dead * 0.6

        # Score relative to resources: maximize over resources
        local_best = -10**18
        for rx, ry in resources:
            ds = abs(rx - nx) + abs(ry - ny)
            do = abs(rx - ox) + abs(ry - oy)
            adv = (do - ds)  # positive means we are closer
            # Encourage taking resources we are already closer to; also deny when behind.
            # Use a saturating-like term via reciprocal distance (deterministic, simple).
            denom = ds + 1
            local = adv * 5.0 + (10.0 / denom) - (ds * 0.05)
            local_best = local if local > local_best else local_best
        move_score += local_best

        # Small tie-break toward reducing distance to nearest resource
        if move_score > best_score:
            best_score = move_score
            best_move = [mdx, mdy]
        elif move_score == best_score:
            cur_near = min(abs(rx - sx) + abs(ry - sy) for rx, ry in resources)
            nxt_near = min(abs(rx - nx) + abs(ry - ny) for rx, ry in resources)
            if nxt_near < cur_near:
                best_move = [mdx, mdy]

    # Ensure return is always valid; if not found (shouldn't), stay.
    nx, ny = sx + best_move[0], sy + best_move[1]
    if valid(nx, ny):
        return best_move
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if valid(nx, ny):
            return [mdx, mdy]
    return [0, 0]