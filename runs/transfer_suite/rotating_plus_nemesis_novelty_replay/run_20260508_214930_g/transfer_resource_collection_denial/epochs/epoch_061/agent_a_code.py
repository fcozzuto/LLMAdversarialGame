def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick target: prefer we are closer, then prefer closer overall, then farther from opponent
    best_t = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        key = (sd - od, sd, -od, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Move selection: avoid obstacles/bounds; minimize distance to target;
    # also keep some separation from opponent; add tie-break toward progress.
    best_move = [0, 0]
    best_val = None
    opp_dist = cheb(sx, sy, ox, oy)

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obs:
                continue

            d_target = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)

            # Encourage getting on/near target and discourage letting opponent get closer.
            val = (d_target * 10 + (0 if (d_target == 0) else 1),
                   -d_opp,
                   -((nx - sx) + (ny - sy)),
                   nx, ny)

            # If we are already very close to opponent, prioritize separation slightly.
            if opp_dist <= 2:
                val = (val[0] + (0 if d_opp >= opp_dist else 2), val[1], val[2], val[3], val[4])

            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move