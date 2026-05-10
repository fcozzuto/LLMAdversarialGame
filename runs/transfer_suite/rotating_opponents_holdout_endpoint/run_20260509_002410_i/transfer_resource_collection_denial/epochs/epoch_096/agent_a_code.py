def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        best = None
        best_val = None
        for rx, ry in resources:
            d_me = man(sx, sy, rx, ry)
            d_op = man(ox, oy, rx, ry)
            # Prefer guaranteed/likely faster grabs; otherwise still take closest.
            # Higher is better.
            if d_me < d_op:
                val = (d_op - d_me + 1) * 200000 - d_me * 10
            elif d_me == d_op:
                val = 100000 - d_me * 10
            else:
                val = -d_me * 1000 - (d_me - d_op)
            if best is None or val > best_val:
                best = (rx, ry); best_val = val
        tx, ty = best
    else:
        tx = (w - 1) // 2
        ty = (h - 1) // 2

    candidates = []
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    # Try diagonal-first, then straight, then stay.
    for mx in [dx]:
        for my in [dy, 0, -dy]:
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append([mx, my])
    # Add pure axis alternatives and stay if needed
    for mx, my in [(dx, 0), (0, dy), (0, 0)]:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append([mx, my])

    if not candidates:
        return [0, 0]

    # Choose candidate that maximizes advantage toward the chosen target.
    best_move = candidates[0]
    best_score = None
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        d_me = man(nx, ny, tx, ty)
        d_op = man(ox, oy, tx, ty)
        if d_me < d_op:
            score = (d_op - d_me + 1) * 100000 - d_me
        elif d_me == d_op:
            score = 50000 - d_me
        else:
            score = -d_me * 1000 - (d_me - d_op)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [mx, my]

    return [int(best_move[0]), int(best_move[1])]