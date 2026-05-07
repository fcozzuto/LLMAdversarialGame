def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer "deniable races": we arrive no later (or within 1), with earliest arrival.
        if sd <= od + 1:
            key = (0, sd, -od, rx, ry)
        else:
            # Otherwise, still prefer resources where we can gain time vs opponent.
            key = (1, -((od - sd) * 100 - sd), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    bestm = (0, 0)
    bestm_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        sd2 = cheb(nx, ny, rx, ry)
        od2 = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to target. Secondary: increase distance from opponent to reduce contest.
        key = (sd2, -od2, abs(dx) + abs(dy))
        if bestm_key is None or key < bestm_key:
            bestm_key = key
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]