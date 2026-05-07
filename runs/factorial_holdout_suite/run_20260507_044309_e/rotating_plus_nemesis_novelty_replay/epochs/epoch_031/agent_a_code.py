def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)
    if not res:
        return [0, 0]

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer being closer; then being nearer overall; then deterministic coord order
        key = (-(do - ds), ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Candidate moves (deterministic order)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        hit_ob = (nx, ny) in obstacles
        # Prefer not hitting obstacles, then decreasing distance to target, then deterministic tie-break
        dist = cheb(nx, ny, tx, ty)
        score = (1 if hit_ob else 0, dist, abs(tx - nx) + abs(ty - ny), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    # If we filtered all moves due to bounds, fallback
    if best_score is None:
        return [0, 0]
    return best_move