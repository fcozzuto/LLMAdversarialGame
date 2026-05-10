def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_toward(ax, ay, bx, by):
        dx = 0 if bx == ax else (1 if bx > ax else -1)
        dy = 0 if by == ay else (1 if by > ay else -1)
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = ax, ay
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0:
                        continue
                    tx, ty = ax + ddx, ay + ddy
                    if inb(tx, ty) and (tx, ty) not in obs:
                        if (tx - bx) * (tx - bx) + (ty - by) * (ty - by) < (nx - bx) * (nx - bx) + (ny - by) * (ny - by):
                            nx, ny = tx, ty
        return nx, ny

    # Predict opponent move assuming it goes toward our current position.
    podx, pody = ox, oy
    po2x, po2y = step_toward(podx, pody, sx, sy)

    best = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Primary: get close to predicted opponent position.
        d_pred = (nx - po2x) * (nx - po2x) + (ny - po2y) * (ny - po2y)
        # Secondary: also keep closer to current opponent (avoid oscillations).
        d_now = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Tertiary: prefer progress along diagonal if tied.
        prog = -(dx * dy)  # deterministic tiebreaker
        key = (d_pred, d_now, abs(dx) + abs(dy), prog)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]