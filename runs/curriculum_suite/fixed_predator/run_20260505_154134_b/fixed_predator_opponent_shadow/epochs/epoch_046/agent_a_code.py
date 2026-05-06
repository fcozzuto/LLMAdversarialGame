def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def pick_target():
        if not resources:
            return None
        best = None
        best_key = None
        for cx, cy in resources:
            self_d = cheb(sx, sy, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # Prefer cells where opponent is already closer; tie-break deterministically.
            key = (opp_d - self_d, -self_d, cx, cy)
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best

    target = pick_target()
    if target is None:
        return [0, 0]
    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Primary: reduce our distance; Secondary: increase chance opponent can't take next;
        # Tertiary: deterministic preference to avoid oscillation (favor toward target axes).
        axis_bias = (abs(nx - tx) - abs(sx - tx)) + (abs(ny - ty) - abs(sy - ty))
        # Slightly penalize moving away from current direction to the target.
        away_pen = (my_d - cheb(sx, sy, tx, ty))
        key = (-my_d, opp_d - my_d, -axis_bias, -away_pen, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]