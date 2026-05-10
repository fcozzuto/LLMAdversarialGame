def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best_res = None
    best_key = None
    for r in resources:
        rx, ry = r
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (od - sd, -sd, rx, ry)  # prefer we are closer; then quicker; then deterministic
        if best_key is None or key > best_key:
            best_key = key
            best_res = r

    rx, ry = best_res
    step_dx = 0 if rx == sx else (1 if rx > sx else -1)
    step_dy = 0 if ry == sy else (1 if ry > sy else -1)
    desired = (sx + step_dx, sy + step_dy)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            nd = dist(nx, ny, rx, ry)
            # also score closeness to desired cell to avoid ties wandering
            des_dist = dist(nx, ny, desired[0], desired[1])
            candidates.append((( -nd, des_dist, dx, dy), nd))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: t[0], reverse=False)
    # smallest -nd means largest nd? We used -nd; so sort by tuple with -nd ascending gives closest
    # Fix: pick min of first tuple where -nd smallest (most negative) => smallest; better to sort by first tuple.
    best = min(candidates, key=lambda t: t[0])[0]
    return [best[2], best[3]]