def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obs_pen(px, py):
        if not obstacles:
            return 0
        best = 999
        for ax, ay in obstacles:
            d = cheb(px, py, ax, ay)
            if d < best:
                best = d
        return 0 if best > 2 else (3 - best) * 2

    best_target = None
    best_score = -10**9
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        score = (od - sd) * 10 - sd - near_obs_pen(tx, ty)
        if score > best_score:
            best_score = score
            best_target = (tx, ty)

    tx, ty = best_target
    best_move = (0, 0)
    best_val = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                opp_d = cheb(ox, oy, tx, ty)
                lead = (opp_d - d)
                block = near_obs_pen(nx, ny)
                val = lead * 10 - d - block
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]