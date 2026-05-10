def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_set = set()
    for t in observation.get("obstacles") or []:
        try:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except:
            pass

    resources = []
    for t in observation.get("resources") or []:
        try:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    resources = resources[:12]
    # Prefer resources where we're ahead; tie-break by being closer.
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    best_m = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        ds2 = manh(nx, ny, rx, ry)
        do2 = manh(ox, oy, rx, ry)
        # Also add slight preference to keep moving toward opponent-competitive advantage.
        # and avoid stepping away when equally competitive.
        step_key = (ds2 - do2, ds2, abs(nx - rx) + abs(ny - ry), dx, dy)
        if best_mkey is None or step_key < best_mkey:
            best_mkey = step_key
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]