def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick target that we can reach sooner (or where opponent is farther).
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (sd - od, sd, abs(rx - (w - 1 - sx)) + abs(ry - (h - 1 - sy)))
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))

    # Choose move that maximizes progress to target while also discouraging stepping closer to opponent.
    best_move = None
    for dx, dy, nx, ny in legal:
        new_sd = man(nx, ny, tx, ty)
        new_od = man(nx, ny, ox, oy)
        # Prefer reducing distance to target; tie-break prefer increasing distance from opponent.
        val = (new_sd, -new_od, abs(dx) + abs(dy))
        if best_move is None or val < best_move[0]:
            best_move = (val, [dx, dy])
    return best_move[1]