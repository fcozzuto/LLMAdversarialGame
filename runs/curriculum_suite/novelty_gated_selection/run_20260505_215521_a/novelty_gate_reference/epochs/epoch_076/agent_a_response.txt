def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target_for_pos(px, py):
        # choose resource maximizing opponent delay; tie-break by faster self arrival
        best = None
        best_key = None
        for tx, ty in resources:
            sd = cheb(px, py, tx, ty)
            od = cheb(ox, oy, tx, ty)
            key = (od - sd, -sd)  # larger advantage, then smaller self distance
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        return best, best_key

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy
        tx, _ = best_target_for_pos(nx, ny)
        if tx is None:
            continue
        sd = cheb(nx, ny, tx[0], tx[1])
        od = cheb(ox, oy, tx[0], tx[1])
        # also favor keeping near center and slightly avoiding positions adjacent to opponent
        center = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
        opp_close = cheb(nx, ny, ox, oy)
        key = (od - sd, -sd, -center, opp_close)
        candidates.append((key, (nx - sx), (ny - sy)))

    # deterministic tie-break: lexicographic on move deltas
    candidates.sort(key=lambda t: (t[0][0], t[0][1], t[0][2], t[0][3], -t[1], -t[2]), reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])] if candidates else [0, 0]