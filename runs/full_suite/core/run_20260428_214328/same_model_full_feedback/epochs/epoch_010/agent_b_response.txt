def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        # Prefer resources where we are at least as close as opponent; if none, pick least favorable to them.
        best = None
        for x, y in resources:
            dme = cheb(sx, sy, x, y)
            dome = cheb(ox, oy, x, y)
            # Primary: minimize our distance among those we can reach first/tie.
            # Secondary: among ties, maximize opponent slack (so they likely can't steal after).
            # Tertiary: deterministic tie-break by coordinates.
            if dme <= dome:
                key = (0, dme, -(dome - dme), (x + y), x, y)
            else:
                # If none reachable-first chosen, we will still pick some: maximize our disadvantage to contest? keep stable.
                key = (1, dme, (dme - dome), (x + y), x, y)
            if best is None or key < best[0]:
                best = (key, (x, y))
        tx, ty = best[1]
    else:
        tx, ty = (w // 2, h // 2)

    # Choose move that avoids obstacles and most reduces distance; slight bias to intercept (closer to opponent).
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_from_t = cheb(sx, sy, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        # Prefer strictly reducing target distance; otherwise minimal distance to target.
        key = (0 if d_to_t < d_from_t else 1, d_to_t, -d_op, (nx, ny))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_key is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]