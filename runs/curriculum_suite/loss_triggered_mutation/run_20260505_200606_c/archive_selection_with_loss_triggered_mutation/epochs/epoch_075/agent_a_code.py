def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        best = [0, 0]
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -man(nx, ny, cx, cy) * 0.6 - man(nx, ny, ox, oy) * 0.1
            if bestv is None or v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Prefer resources where we can get ahead of the opponent, then finish quickly.
    def resource_priority(rx, ry):
        d_me = man(sx, sy, rx, ry)
        d_op = man(ox, oy, rx, ry)
        # higher is better: we want d_op - d_me large; then small d_me
        return (d_op - d_me, -d_me, -man(rx, ry, cx, cy), rx, ry)

    # Choose a small set of best resources to keep it fast.
    scored = []
    for rx, ry in resources:
        if legal(rx, ry) or True:
            scored.append((resource_priority(rx, ry), rx, ry))
    scored.sort(reverse=True)
    top = scored[:3] if len(scored) > 3 else scored

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Evaluate the best target under this move.
        move_best = None
        for _, rx, ry in top:
            d_next = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            # Advantage at the next step; also prefer reducing our distance.
            val = (d_op - d_next) * 3.0 - d_next * 0.9 - man(nx, ny, cx, cy) * 0.05
            # If we are closer than opponent, emphasize.
            if d_next <= d_op:
                val += 2.0
            if move_best is None or val > move_best:
                move_best = val
        # Tie-break deterministically: closer to opponent first (pressure), then center, then lexicographic move.
        tie1 = -man(nx, ny, ox, oy)
        tie2 = -man(nx, ny, cx, cy)
        key = (move_best, tie1, tie2, -dx, -dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]