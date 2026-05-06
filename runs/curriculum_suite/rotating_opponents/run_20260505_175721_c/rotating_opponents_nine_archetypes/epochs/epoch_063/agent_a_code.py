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

    def diag_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
    else:
        best = None
        best_pos = None
        best_adv = None
        for rx, ry in resources:
            self_d = diag_dist(sx, sy, rx, ry)
            opp_d = diag_dist(ox, oy, rx, ry)
            adv = opp_d - self_d  # positive means we are closer in diagonal metric
            key = (adv, -self_d, -abs(rx - ox) - abs(ry - oy), rx, ry)
            if best is None or key > best:
                best = key
                best_pos = (rx, ry)
                best_adv = adv
        if best_adv is not None and best_adv <= 0:
            # Intercept: pick resource with smallest opponent distance (most likely target)
            tx, ty = min(resources, key=lambda r: (diag_dist(ox, oy, r[0], r[1]), diag_dist(sx, sy, r[0], r[1]), r[0], r[1]))
        else:
            tx, ty = best_pos

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_d = diag_dist(sx, sy, tx, ty)

    # Prefer moves that reduce distance to target; avoid obvious obstacle cells if possible.
    best_move = (0, 0)
    best_score = (-10**9, 0)  # (score, x_then_y)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = diag_dist(nx, ny, tx, ty)
        improvement = cur_d - nd
        score = (improvement, -nd, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move == (0, 0):
        # If all forward moves were blocked, allow staying.
        return [0, 0]
    return [best_move[0], best_move[1]]