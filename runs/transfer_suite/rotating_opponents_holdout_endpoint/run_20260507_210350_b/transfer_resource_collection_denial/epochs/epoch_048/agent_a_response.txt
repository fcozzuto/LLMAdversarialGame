def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not (0 <= rx < w and 0 <= ry < h):
            continue
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        diff = opp_d - our_d  # >0 means we are closer
        # Prefer guaranteed-ish captures: positive diff, then smallest our_d, then largest diff
        key = (0 if diff > 0 else 1, our_d, -diff, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best
    dx = tx - sx
    dy = ty - sy

    def try_step(nx, ny, cx, cy):
        if (nx, ny) in obstacles:
            return None
        if not (0 <= nx < w and 0 <= ny < h):
            return None
        return (cheb(nx, ny, tx, ty), (cx, cy))

    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0 and (dx != 0 or dy != 0):
                continue
            nx, ny = sx + mx, sy + my
            res = try_step(nx, ny, mx, my)
            if res is not None:
                candidates.append(res)

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], abs(sx + t[1][0] - ox) - abs(sx - ox), -t[1][0], -t[1][1]))
    return [int(candidates[0][1][0]), int(candidates[0][1][1])]