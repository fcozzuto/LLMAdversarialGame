def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; then those we beat by margin; then deterministic position.
            key = (ds, -(do - ds), rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        if best is None:
            return (w // 2, h // 2)
        return best[1]

    tx, ty = best_target()
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_us = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # Move that most reduces our distance; if tie, prefer not helping opponent.
        key = (d_us, (d_us + 1) if (d_op <= d_us) else 0, rx if False else 0)
        # Above line keeps determinism without extra state; will be overwritten by proper tie-break below.
        key = (d_us, -cheb(nx, ny, ox, oy), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]] if best_move else [0, 0]