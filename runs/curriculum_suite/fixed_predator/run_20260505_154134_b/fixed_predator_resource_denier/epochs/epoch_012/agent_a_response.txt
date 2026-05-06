def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def add_step(tx, ty):
        best = [0, 0]
        best_key = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                ds_t = cheb(nx, ny, tx, ty)
                ds_o = cheb(nx, ny, ox, oy)
                # Prefer reducing distance to target; if tie, move to worsen opponent access.
                key = (-ds_t, ds_o, dx, dy)
                if best_key is None or key > best_key:
                    best_key = key
                    best = [dx, dy]
        return best

    if resources:
        # Pick the resource that maximizes (opponent advantage) and is reachable soonest for us.
        best_r = None
        best_v = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            da = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Strongly favor resources we can reach no later than opponent.
            v = (do - da, -da, rx, ry)
            if best_v is None or v > best_v:
                best_v = v
                best_r = (rx, ry)
        if best_r is not None:
            tx, ty = best_r
            return add_step(tx, ty)

    # No usable resources: deny by moving to reduce distance to opponent.
    # If already adjacent, stay (deterministic), else step toward them.
    d = cheb(sx, sy, ox, oy)
    if d <= 1:
        return [0, 0]
    # Choose direction that minimizes distance to opponent while avoiding obstacles.
    return add_step(ox, oy)