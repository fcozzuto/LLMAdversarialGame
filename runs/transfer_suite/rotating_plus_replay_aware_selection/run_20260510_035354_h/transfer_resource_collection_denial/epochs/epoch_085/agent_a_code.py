def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def adj_block_pen(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obs:
                    cnt += 1
        return cnt

    same_row_bias = 1 if "row" in opp_role or "row" in self_role else 0
    my_dominance = 0.85 if "nearest" in opp_role else 0.95

    best = None
    best_val = None
    for rx, ry in res:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lane = same_row_bias * (1 if ry == sy else 0)
        val = md - od * my_dominance + 0.15 * adj_block_pen(rx, ry) - 0.25 * lane
        if best is None or val < best_val or (val == best_val and (rx < best[0] or (rx == best[0] and ry < best[1]))):
            best_val = val
            best = (rx, ry)

    tx, ty = best
    step_dx = 0 if tx == sx else (1 if tx > sx else -1)
    step_dy = 0 if ty == sy else (1 if ty > sy else -1)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    cand = []
    cand.append((step_dx, step_dy))
    cand.append((step_dx, 0))
    cand.append((0, step_dy))
    cand.append((step_dx, -step_dy))
    cand.append((0, 0))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            if (dx, dy) not in [(c[0], c[1]) for c in cand]:
                cand.append((dx, dy))

    best_move = (0, 0)
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = cheb(nx, ny, tx, ty)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]