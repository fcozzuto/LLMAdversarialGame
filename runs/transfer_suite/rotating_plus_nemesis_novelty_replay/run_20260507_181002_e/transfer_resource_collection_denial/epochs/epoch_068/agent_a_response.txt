def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Resource_denier counter: pick a resource by distance margin (deny first if possible)
    best_r = None
    best_key = None
    for x, y in resources:
        sd = md(sx, sy, x, y)
        od = md(ox, oy, x, y)
        key = (od - sd, -sd)  # maximize margin; if tied, smaller self distance
        if best_key is None or key > best_key:
            best_key = key
            best_r = (x, y)

    tx, ty = best_r
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_obj = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd_new = md(nx, ny, tx, ty)
        # Prefer moves that improve your position vs the chosen resource margin
        sd_now = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        margin_new = od - sd_new
        obj = (sd_new, -margin_new, abs(nx - tx) + abs(ny - ty), 0 if (dx == 0 and dy == 0) else 1)
        if best_obj is None or obj < best_obj:
            best_obj = obj
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]