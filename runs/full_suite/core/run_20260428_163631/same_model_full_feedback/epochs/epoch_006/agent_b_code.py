def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic preference order: center-staying, then closer to (0,0) delta magnitude, then fixed.
    deltas.sort(key=lambda d: (d[0] == 0 and d[1] == 0, d[0]*d[0]+d[1]*d[1], d[0], d[1]))

    # If no resources, deterministically chase: move to reduce distance to opponent.
    if not resources:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not safe(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            key = (d, -dx, -dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]

    best_overall = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        # Choose the resource that maximizes our advantage from next position,
        # with a penalty if opponent is predicted to be much closer.
        best_res_key = None
        for rx, ry in resources:
            if not inb(rx, ry):
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - sd  # positive => we are closer
            # Also prefer resources that are closer to us (smaller sd) when gaps tie.
            # Penalize if opponent is close regardless (od small).
            pred_pen = 0
            if od <= sd:
                pred_pen = (sd - od) + 2  # discourage letting opponent have the same/greater claim
            key = (-gap, sd + pred_pen, od, rx, ry)
            if best_res_key is None or key < best_res_key:
                best_res_key = key

        # Prefer moves that maximize best resource key; deterministic fallback uses distance to best target implicitly.
        if best_res_key is None:
            continue
        # Convert key to overall comparison directly (smaller is better).
        if best_overall is None or best_res_key < best_overall[0]:
            best_overall = (best_res_key, dx, dy)

    if best_overall is None:
        return [0, 0]
    return [int(best_overall[1]), int(best_overall[2])]