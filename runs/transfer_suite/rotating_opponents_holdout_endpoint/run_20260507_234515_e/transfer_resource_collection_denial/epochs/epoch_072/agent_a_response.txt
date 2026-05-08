def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in res:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        risk = dS - dO  # smaller => more likely to arrive first
        # Also prefer resources closer to our x direction and slightly away from opponent
        key = (risk, dS, -(abs(rx - sx) + abs(ry - sy)), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # avoid stepping closer to opponent if it doesn't improve our target progress
        dS_next = cheb(nx, ny, tx, ty)
        dO_next = cheb(nx, ny, ox, oy)
        dO_cur = cheb(sx, sy, ox, oy)
        progress = dS_next
        # tie-break: if opponent closer to target, prefer moves that increase their distance to that target
        opp_to_target = cheb(ox, oy, tx, ty)
        opp_if_denied = cheb(ox, oy, tx, ty)  # static heuristic
        # score key: prioritize reaching target first, then closeness, then safety from opponent proximity
        key = (progress, dO_next - dO_cur, -opp_if_denied, nx, ny)
        if bestk is None or key < bestk:
            bestk = key
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]