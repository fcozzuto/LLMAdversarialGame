def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def best_step(tx, ty):
        if sx == tx and sy == ty:
            return [0, 0]
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # Prefer smaller distance; deterministic tie-breaking by move order encoded in moves list.
            k = (d, dx, dy)
            if best is None or k < best[0]:
                best = (k, [dx, dy])
        return best[1] if best else [0, 0]

    if resources:
        # Target resources where we have the largest arrival advantage over the opponent.
        best_target = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_s = cheb(sx, sy, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            adv = d_o - d_s  # bigger is better
            # Primary: maximize adv -> minimize -adv. Secondary: smaller our distance.
            # Tertiary: deterministic by position.
            key = (-adv, d_s, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_target = (rx, ry)
        if best_target is not None:
            return best_step(best_target[0], best_target[1])

    # Fallback: head to a robust midpoint while avoiding obstacles.
    tx, ty = w // 2, h // 2
    return best_step(tx, ty)