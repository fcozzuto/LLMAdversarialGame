def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = ox, oy
    else:
        # race evaluation: prefer resources where we are significantly closer
        # if we are generally behind, flip to avoid resources opponent is likely to take
        best = None
        best_score = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gain = do - ds  # positive means we are closer
            if best is None:
                best = (rx, ry)
                best_score = gain
            else:
                # if behind (all gains <=0), choose most negative (worst for opponent / best for avoidance)
                # deterministically switch criterion based on current best gain sign.
                if best_score <= 0 and gain <= 0:
                    if gain > best_score:
                        best = (rx, ry); best_score = gain
                else:
                    if gain > best_score or (gain == best_score and (rx, ry) < best):
                        best = (rx, ry); best_score = gain
        tx, ty = best

    # choose move maximizing progress to target; keep away from obstacles edges via inside-check
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ds_new = cheb(nx, ny, tx, ty)
        ds_cur = cheb(sx, sy, tx, ty)
        # deterministic tie-break also considers opponent distance (to reduce giving them easy steals)
        do_cur = cheb(ox, oy, tx, ty)
        do_new = cheb(ox, oy, tx, ty)
        val = (ds_cur - ds_new) * 100 - ds_new
        val += (do_new - do_cur) * 0  # no-op, keeps deterministic structure
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]