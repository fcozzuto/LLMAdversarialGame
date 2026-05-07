def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res or (sx, sy) in obst:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_key(px, py):
        best = None
        for tx, ty in res:
            sd = cheb(px, py, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # maximize win margin; then prefer closer; then deterministic order
            key = (od - sd, -sd, (tx + 31 * ty) % 997)
            if best is None or key > best[0]:
                best = (key, tx, ty)
        return best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur = best_key(sx, sy)
    target_tx, target_ty = cur[1], cur[2]

    chosen = None
    chosen_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        nxt = best_key(nx, ny)
        key = nxt[0]
        # slight preference for moving toward the current best target
        tie2 = cheb(nx, ny, target_tx, target_ty)
        val = (key[0], key[1], -tie2, key[2])
        if chosen is None or val > chosen_val:
            chosen = [dx, dy]
            chosen_val = val

    return chosen if chosen is not None else [0, 0]