def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles
    def best_target_for(px, py):
        if not resources:
            return (w // 2, h // 2), 10**9
        best_t = None
        best_key = None
        best_ds = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            behind = ds - do  # <= -1 => we are closer
            # Prefer resources we can get first; otherwise closest resource we can still contest.
            key = (0 if behind <= -1 else 1, ds, behind, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
                best_ds = ds
        if best_t is None:
            return (w // 2, h // 2), 10**9
        return best_t, best_ds
    cur_t, cur_ds = best_target_for(sx, sy)
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        t, ds = best_target_for(nx, ny)
        rx, ry = t
        # Score: reduce distance to chosen target; also slightly discourage moving away from current best target.
        move_score = (ds, cheb(nx, ny, rx, ry), -cheb(nx, ny, ox, oy), rx, ry)
        if best_score is None or move_score < best_score:
            best_score = move_score
            best_move = [dx, dy]
    return best_move