def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_key = None
        for (tx, ty) in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer targets where we are relatively closer than opponent.
            # Key: maximize lead, then minimize our distance, then deterministic by coords.
            key = (od - sd, -sd, -tx, -ty)
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
        sd0 = cheb(sx, sy, tx, ty)
        od0 = cheb(ox, oy, tx, ty)

        best_move = (0, 0)
        best_mkey = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)  # opponent unchanged this turn
            # Primary: reduce our distance to target.
            # Secondary: keep distance from opponent (avoid being cornered).
            # Tertiary: avoid wasting moves with no progress.
            opp_dist = cheb(nx, ny, ox, oy)
            mkey = (-sd, -opp_dist, -int(sd < sd0), -int(sd == sd0 and (dx != 0 or dy != 0)), dx, dy)
            if best_mkey is None or mkey > best_mkey:
                best_mkey = mkey
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # No resources: deterministic drift toward opponent side but keep away from obstacles best-effort.
        driftx, drifty = (sx + (1 if ox > sx else -1 if ox < sx else 0), sy + (1 if oy > sy else -1 if oy < sy else 0))
        tx, ty = driftx, drifty
        best_move = (0, 0)
        best_mkey = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            mkey = (-cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), dx, dy)
            if best_mkey is None or mkey > best_mkey:
                best_mkey = mkey
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]