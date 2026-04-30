def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            score = ds - 0.6 * do  # prioritize nearer / deny if opponent is closer
            if best is None or score < best[0] or (score == best[0] and (rx, ry) < best[1]):
                best = (score, (rx, ry))
        tx, ty = best[1]
        best_move = None
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            val = cheb(nx, ny, tx, ty)
            # tiny tie-breaker to be deterministic
            tie = (val, abs(nx - tx) + abs(ny - ty), dx, dy)
            if best_val is None or tie < best_val:
                best_val = tie
                best_move = [dx, dy]
        if best_move is not None:
            return best_move
    # Fallback: head toward opponent to contest center/resources
    best_move = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        val = cheb(nx, ny, ox, oy)
        tie = (val, dx, dy)
        if best_val is None or tie < best_val:
            best_val = tie
            best_move = [dx, dy]
    return best_move if best_move is not None else [0, 0]