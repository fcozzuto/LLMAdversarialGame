def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = [(dx, dy) for dx, dy in moves if free(sx + dx, sy + dy)]
    if not cand:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # If evading: prefer the farthest corner that is not obviously blocked.
    # If pursuing: move to reduce distance to opponent; avoid repeating obvious stalls.
    if is_evader:
        def corner_key(c):
            return md(ox, oy, c[0], c[1])  # run toward corner far from pursuer
        target = max(corners, key=corner_key)
    else:
        target = (ox, oy)

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if is_evader:
            # maximize distance from pursuer; keep toward a chosen corner by small bias
            d = md(nx, ny, ox, oy)
            cb = -md(nx, ny, target[0], target[1])
            center_pen = abs(nx - cx) + abs(ny - cy)
            return (d, cb, -center_pen)  # lexicographic maximize
        else:
            d = md(nx, ny, ox, oy)
            # slight bias to cornering/closing along axes without heavy computation
            toward_corner = max(corners, key=lambda c: -md(nx, ny, c[0], c[1]))
            corner_bias = -md(nx, ny, toward_corner[0], toward_corner[1])
            center_pen = abs(nx - cx) + abs(ny - cy)
            return (-d, corner_bias, -center_pen)  # lexicographic maximize

    best = None
    best_s = None
    for dx, dy in cand:
        s = score_move(dx, dy)
        if best_s is None or s > best_s:
            best_s, best = s, (dx, dy)

    return [int(best[0]), int(best[1])]