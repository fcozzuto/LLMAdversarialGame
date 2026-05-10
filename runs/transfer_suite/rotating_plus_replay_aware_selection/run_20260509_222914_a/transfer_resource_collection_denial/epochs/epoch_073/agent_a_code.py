def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def md(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx + dy

    def target_value(px, py):
        best = None
        for rx, ry in resources:
            sd = md(px, py, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer cells where we are closer than opponent; then faster self.
            v = (od - sd, -sd)
            if best is None or v > best:
                best = v
        return best[0], -best[1]

    best_move = (0, 0)
    best_v = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        advantage, selfdist = target_value(nx, ny)
        # Tie-break: minimize distance to best resource, and also prefer moves toward opponent side less.
        v = (advantage, -selfdist, -md(nx, ny, ox, oy))
        if best_v is None or v > best_v:
            best_v = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]