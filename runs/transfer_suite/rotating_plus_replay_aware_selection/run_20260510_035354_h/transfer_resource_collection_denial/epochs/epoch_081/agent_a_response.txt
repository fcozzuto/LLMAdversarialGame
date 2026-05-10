def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target the opponent is more likely to lose relative to us.
    best = None
    best_key = None
    for rx, ry in res:
        sd = cheb_dist(sx, sy, rx, ry)
        od = cheb_dist(ox, oy, rx, ry)
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # One-step tactical evaluation for immediate advantage.
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            nx, ny = sx, sy
        nsd = cheb_dist(nx, ny, tx, ty)
        nod = cheb_dist(ox, oy, tx, ty)
        # Prefer reducing our distance; break ties by increasing our lead over opponent.
        lead = nod - nsd
        score = (lead, -nsd, -abs(nx - ox) - abs(ny - oy), -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move