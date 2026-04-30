def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def man(a, b, c, d):
        v1 = a - c
        if v1 < 0: v1 = -v1
        v2 = b - d
        if v2 < 0: v2 = -v2
        return v1 + v2

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))

    if not cand:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = man(nx if False else x, y, rx, ry)
            od = man(x, y, ox, oy)  # dummy overwritten below
            od = man(ox, oy, rx, ry)
            key = (od - sd, -sd, rx, ry)
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        tx, ty = cx, cy

    def score_move(dx, dy, nx, ny):
        d_to = man(nx, ny, tx, ty)
        d_from_opp = man(nx, ny, ox, oy)
        if resources:
            # Prefer moves that improve relative access to the target resource
            rel_now = man(x, y, tx, ty) - man(ox, oy, tx, ty)
            rel_next = d_to - d_from_opp
            return (-(rel_next), d_to, -d_from_opp)
        return (d_to, -d_from_opp)

    bestm = None
    bestk = None
    for dx, dy, nx, ny in cand:
        k = score_move(dx, dy, nx, ny)
        if bestm is None or k < bestk:
            bestm = (dx, dy)
            bestk = k

    return [int(bestm[0]), int(bestm[1])]