def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                resources.append((x, y))

    def dist_cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def best_resource():
        if not resources:
            return None
        best = None
        best_key = None
        for tx, ty in resources:
            ds = dist_cheb(sx, sy, tx, ty)
            do = dist_cheb(ox, oy, tx, ty)
            # Prefer: we can arrive much earlier; then earlier arrival; then toward center-ish
            center_bias = - (abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2))
            key = (do - ds, -ds, center_bias)
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        return best

    target = best_resource()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # If no target, just drift toward opponent's side while staying safe
    if target is None:
        desired = (w - 1 if ox < sx else 0, h - 1 if oy < sy else 0)
        tx, ty = desired[0], desired[1]
        def score_move(nx, ny):
            return (-dist_cheb(nx, ny, tx, ty), -dist_cheb(nx, ny, ox, oy))
    else:
        tx, ty = target[0], target[1]
        def score_move(nx, ny):
            ds2 = dist_cheb(nx, ny, tx, ty)
            do2 = dist_cheb(ox, oy, tx, ty)
            # If opponent can also take it soon, prefer moves that increase their effective disadvantage
            opp_pressure = do2 - ds2
            # Avoid stepping into "tight" squares next to opponent (softly)
            opp_adj = - (dist_cheb(nx, ny, ox, oy) == 0) - 0.5 * (dist_cheb(nx, ny, ox, oy) == 1)
            return (opp_pressure, -ds2, opp_adj, -(abs(nx - tx) + abs(ny - ty)))

    best_dm = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        val = score_move(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_dm = (dx, dy)

    return [int(best_dm[0]), int(best_dm[1])]