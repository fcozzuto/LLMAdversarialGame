def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                seen.add((x, y))
                res.append((x, y))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    def score_to_target(nx, ny, tx, ty):
        dx = nx - tx
        if dx < 0: dx = -dx
        dy = ny - ty
        if dy < 0: dy = -dy
        return dx + dy

    best_move = (0, 0)
    best_val = 10**18
    target = None

    if res:
        # Choose the move that minimizes distance to the nearest resource (deterministic tie-break).
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            m = 10**18
            for rx, ry in res:
                d = score_to_target(nx, ny, rx, ry)
                if d < m:
                    m = d
            # Small penalty for being close to opponent to encourage safer resource grabs.
            od = score_to_target(nx, ny, ox, oy)
            val = m * 1000 + (20 - od if od < 20 else 0)
            if val < best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        # No known resources: move away from opponent if close, else move toward opponent to contest.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = score_to_target(nx, ny, ox, oy)
            val = d
            if val < best_val:
                best_val = val
                best_move = [dx, dy]
        # If we never found a valid move (unlikely), stay.
        if best_move == (0, 0) and not inside(sx, sy):
            best_move = [0, 0]

    # Ensure return type and validity range.
    return [int(best_move[0]), int(best_move[1])]