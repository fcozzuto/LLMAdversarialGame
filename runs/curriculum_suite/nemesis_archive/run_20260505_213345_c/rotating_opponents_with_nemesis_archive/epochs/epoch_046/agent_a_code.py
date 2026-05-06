def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    center = (w // 2, h // 2)
    best = None  # (key, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        my_c = dist((nx, ny), center)
        best_delta = None
        best_m = None
        best_o = None
        for r in resources:
            myd = dist((nx, ny), r)
            od = dist((ox, oy), r)
            delta = myd - od  # negative means we are closer (intercept race)
            if best_delta is None or delta < best_delta or (delta == best_delta and myd < best_m):
                best_delta, best_m, best_o = delta, myd, od

        # Main: maximize lead by choosing move with smallest delta; tie-break by our distance and by opponent distance.
        # Secondary: prefer slightly closer to center to avoid getting cornered.
        key = (best_delta, best_m, -best_o, my_c, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx if 0 <= nx + 0 else dx, dy)
            # above dx/dy are fine since we didn't change them; keep deterministic

    return [best[1], best[2]] if best else [0, 0]