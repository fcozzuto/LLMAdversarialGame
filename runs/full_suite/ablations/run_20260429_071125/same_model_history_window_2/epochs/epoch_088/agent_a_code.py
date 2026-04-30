def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Pick resource where we can get there sooner (or tie-break by being farther ahead vs opponent)
        best = None
        best_key = None
        for tx, ty in resources:
            myd = cheb(sx, sy, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # minimize (myd - opd) primarily; then myd; then prefer positions closer to board center for tie stability
            center_bias = cheb(tx, ty, (w - 1) // 2, (h - 1) // 2)
            key = (myd - opd, myd, center_bias, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best

    # Greedy step toward target with obstacle handling and opponent-distance tie-break
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_to_target = cheb(nx, ny, tx, ty)
        dist_from_opp = cheb(nx, ny, ox, oy)
        # prefer smaller target distance; then larger opponent distance (deny contest); then deterministic tie-break
        candidates.append((dist_to_target, -dist_from_opp, nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    candidates.sort()
    return [int(candidates[0][4]), int(candidates[0][5])]