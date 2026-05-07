def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not res:
        return [0, 0]

    ox, oy = observation["opponent_position"]

    # Pick a resource to deny: maximize how much closer we are than opponent.
    best = None
    for rx, ry in res:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd, -rx, -ry)  # higher is better; then prefer smaller sd
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # One-step decision: pick move that most improves toward (tx,ty) while avoiding getting closer to opponent on a rival.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                myd = cheb(nx, ny, tx, ty)
                # Opportunistically add a denial term: compare to opponent's distance to the same target.
                od = cheb(ox, oy, tx, ty)
                # Also slight preference to move away from opponent overall to reduce interception.
                oppd = cheb(nx, ny, ox, oy)
                candidates.append((myd, -od, -oppd, dx, dy))

    # If all candidate moves are blocked (should be rare), stay.
    if not candidates:
        return [0, 0]

    candidates.sort()
    _, _, _, dx, dy = candidates[0]
    return [dx, dy]