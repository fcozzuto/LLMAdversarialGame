def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick target to contest: prefer where opponent is closer than us, then shorter distances overall.
    best = None
    best_key = None
    for cx, cy in resources:
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        key = (opp_d - self_d, -self_d, -opp_d, -(cx + cy))
        if best_key is None or key > best_key:
            best_key = key
            best = (int(cx), int(cy))

    tx, ty = best

    # One-step lookahead: evaluate each move by (our dist to target) and whether it reduces opponent's chance.
    best_move = [0, 0]
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            our_d = cheb(nx, ny, tx, ty)

            # approximate opponent next step: move it greedily toward the same target, avoiding obstacles.
            o_best = (ox, oy)
            o_best_d = cheb(ox, oy, tx, ty)
            for odx in (-1, 0, 1):
                for ody in (-1, 0, 1):
                    mx, my = ox + odx, oy + ody
                    if not inb(mx, my) or (mx, my) in obs:
                        continue
                    d = cheb(mx, my, tx, ty)
                    if d < o_best_d or (d == o_best_d and (mx, my) == (nx, ny) and (odx, ody) != (0, 0)):
                        o_best_d = d
                        o_best = (mx, my)
            opp_d_after = o_best_d

            # Prefer moves that reduce our distance while keeping opponent farther.
            val = (opp_d_after - our_d, -our_d, -abs(nx - tx) - abs(ny - ty))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    # If all candidate moves blocked, stay put (engine will keep us if invalid).
    if best_val is None:
        return [0, 0]
    return best_move