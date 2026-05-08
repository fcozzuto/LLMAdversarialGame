def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_t = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources where we are closer than opponent; break ties by smaller self distance
        val = (od - sd) * 100 - sd
        if val > best_score:
            best_score = val
            best_t = (rx, ry)

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_mval = 10**18
    best_ov = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        nsd = man(nx, ny, tx, ty)
        nod = man(ox, oy, tx, ty)
        # Primary: reduce our distance to target; Secondary: make target harder for opponent (more distance for opp relative)
        mval = nsd
        ov = (nod - nsd)
        if mval < best_mval or (mval == best_mval and (ov > best_ov or (ov == best_ov and (dx, dy) < best_m))):
            best_mval = mval
            best_ov = ov
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]