def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    blocked = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = "evad" in self_role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def score_move(nx, ny):
        # capture ends when on same cell; avoid it
        if nx == ox and ny == oy:
            return -10**9 if is_evader else 10**9

        dx = nx - ox
        dy = ny - oy
        d2 = dx * dx + dy * dy

        # pursuer: minimize distance; evader: maximize distance
        if is_evader:
            s = d2
        else:
            s = -d2

        # obstacle-aware: prefer having more legal neighbors (mobility)
        neigh = 0
        for mdx, mdy in moves:
            tx, ty = nx + mdx, ny + mdy
            if ok(tx, ty):
                neigh += 1
        s += neigh * (1.0 if is_evader else 0.5)

        # centrality tie-breaker (slightly)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        s += (-1.0 if is_evader else 1.0) * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.01

        # deterministic directional bias: follow/oppose opponent in sign of delta
        s += (1 if is_evader else -1) * (abs(nx - ox) + abs(ny - oy)) * 1e-3

        return s

    best_s = None
    best_m = [0, 0]
    # deterministic tie-break by move order
    for mdx, mdy in moves:
        nx, ny = x + mdx, y + mdy
        if not ok(nx, ny):
            continue
        s = score_move(nx, ny)
        if best_s is None or s > best_s:
            best_s = s
            best_m = [mdx, mdy]

    return best_m