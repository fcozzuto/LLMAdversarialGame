def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_score(x, y):
        if not res:
            return -10**9
        best = -10**9
        for tx, ty in res:
            sd = cheb(x, y, tx, ty)
            od = cheb(ox, oy, tx, ty)
            margin = od - sd  # >0 means we are closer or equal
            # Prefer winning margin, then being closer sooner, then farther/upper-left tie-break
            val = margin * 100 - sd * 2 - (tx + ty) * 0.0001
            if val > best:
                best = val
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            v = cell_score(nx, ny)
            # tie-break deterministically toward keeping direction stable (smallest dx^2+dy^2 already ok) then lex
            if v > best_val or (v == best_val and (dx, dy) < (best_move[0], best_move[1])):
                best_val = v
                best_move = [dx, dy]

    if best_val == -10**18:
        return [0, 0]
    return best_move