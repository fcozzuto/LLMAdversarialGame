def choose_move(observation):
    def to_int(v, d=0):
        try:
            return int(v)
        except:
            return d
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = to_int(sx), to_int(sy), to_int(ox), to_int(oy)
    w = to_int(observation.get("grid_width", 0), 8) or 8
    h = to_int(observation.get("grid_height", 0), 8) or 8

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax >= ay else ay

    obs_set = set()
    obs = observation.get("obstacles", []) or []
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = to_int(p[0]), to_int(p[1])
            if inb(x, y):
                obs_set.add((x, y))

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = to_int(r[0]), to_int(r[1])
            if inb(x, y) and (x, y) not in obs_set:
                targets.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not targets:
        best_move = [0, 0]
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            key = (cheb(nx, ny, ox, oy), cheb(nx, ny, sx, sy))
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move

    # Choose target deterministically: prefer resources I can reach earlier than opponent, then closest, then tie-break by coordinates.
    best_t = targets[0]
    best_key = None
    for rx, ry in targets:
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (myd <= od, -myd, -((rx * 1000003 + ry) % 1000000), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t

    # Evaluate next move by minimizing distance to target; break ties by maximizing distance from opponent; avoid obstacles and out-of-bounds.
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        key = (cheb(nx, ny, rx, ry), -cheb(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move