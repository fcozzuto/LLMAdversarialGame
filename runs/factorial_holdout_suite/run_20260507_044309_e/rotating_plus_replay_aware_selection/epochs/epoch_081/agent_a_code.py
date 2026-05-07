def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def clamp_target(tx, ty):
        if tx < 0: tx = 0
        elif tx >= w: tx = w - 1
        if ty < 0: ty = 0
        elif ty >= h: ty = h - 1
        return tx, ty
    def best_key_for_pos(px, py):
        if not resources:
            return (0, 0, 0, px, py, 0)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            row_bias = (ry <= oy) - (ry > oy)
            key = (do - ds, -ds, -row_bias, -cheb(px, py, ox, oy), rx, ry)
            if best is None or key > best:
                best = key
        if best is None:
            return (0, 0, 0, px, py, 0)
        return best

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        key = best_key_for_pos(nx, ny)
        # Prefer beating opponent; if tie, prefer smaller travel to the chosen resource; then closer to opponent.
        if best_val is None or key > best_val or (key == best_val and (dx, dy) < best_move):
            best_val = key
            best_move = (dx, dy)

    if best_val is None:
        # If stuck, deterministically try a legal direction toward center.
        tx, ty = clamp_target(w // 2, h // 2)
        dx = 1 if tx > sx else (-1 if tx < sx else 0)
        dy = 1 if ty > sy else (-1 if ty < sy else 0)
        cand = (dx, dy)
        nx, ny = sx + cand[0], sy + cand[1]
        if legal(nx, ny):
            return [cand[0], cand[1]]
        return [0, 0]
    return [best_move[0], best_move[1]]