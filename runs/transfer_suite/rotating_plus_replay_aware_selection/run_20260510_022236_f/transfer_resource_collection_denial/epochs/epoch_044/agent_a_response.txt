def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for a, b in obstacles:
        a, b = int(a), int(b)
        if 0 <= a < w and 0 <= b < h:
            obs.add((a, b))
    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]
    if (sx, sy) in obs:
        return [0, 0]
    if (sx, sy) in res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def pick_target():
        best = None
        best_key = None
        for rx, ry in res:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we are closer to; if tied, prefer smaller our distance.
            # If still tied, prefer deterministic order by coordinates.
            key = (sd - od, sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = pick_target()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        if (nx, ny) == (tx, ty):
            best_val = (-10**9, 0, 0)
            best_move = (dx, dy)
            break

        # Evaluate by how much we reduce our distance to the target, plus avoid moving near obstacles.
        d_now = cheb(sx, sy, tx, ty)
        d_new = cheb(nx, ny, tx, ty)
        progress = d_now - d_new

        near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    near += 1

        # If we can't secure the chosen target, still try to maximize progress.
        val = (-near, -d_new, -progress, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]