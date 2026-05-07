def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def best_for(px, py):
        best_key = None
        for tx, ty in res:
            sd = md(px, py, tx, ty)
            od = md(ox, oy, tx, ty)  # opponent fixed for evaluation
            adv = od - sd
            # strong preference to arrive first; slight preference for farther-from-opponent resources
            key = (adv, -sd, sd - od)
            if best_key is None or key > best_key:
                best_key = key
        if best_key is None:
            return -10**9
        return best_key[0] * 100 - best_key[1]

    # Opponent "pressure" baseline: how well opponent currently can do
    opp_best = None
    for tx, ty in res:
        od = md(ox, oy, tx, ty)
        key = (-od, od)  # smaller od better
        if opp_best is None or key > opp_best:
            opp_best = key
    opp_best_val = -opp_best[0] if opp_best is not None else 0

    cur_my = best_for(sx, sy)
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        my_val = best_for(nx, ny)
        # also reduce opponent's advantage by not moving toward "hot" routes for them
        # compute opponent's best advantage on same step for a rough denial heuristic
        hot = 0
        for tx, ty in res:
            sd = md(nx, ny, tx, ty)
            od = md(ox, oy, tx, ty)
            if od < sd:
                hot += 1
        val = (my_val - cur_my) + (my_val - opp_best_val) - hot * 3 + (-(abs(nx - ox) + abs(ny - oy)) * 0.01)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move