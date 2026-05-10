def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Likely-denied target: closest to opponent; break ties by our distance.
    best_t = None
    best_td = None
    for tx, ty in resources:
        od = cheb(ox, oy, tx, ty)
        sd = cheb(sx, sy, tx, ty)
        key = (od, sd, tx, ty)
        if best_td is None or key < best_td:
            best_td = key
            best_t = (tx, ty)

    tx, ty = best_t
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        sd2 = cheb(nx, ny, tx, ty)
        adv2 = cheb(ox, oy, tx, ty) - sd2  # opponent distance - our distance
        opp_gain = cheb(ox, oy, nx, ny)  # discourage drifting away from opponent lock-in
        key = (-adv2, sd2, -opp_gain, dx, dy)  # max adv2 then min sd2; deterministic tie
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]