def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        dx = 0
        dy = 0
        if w > 1 and sx < w - 1 and (sx + 1, sy) not in obstacles:
            dx = 1
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    best_t = None
    best_score = -10**18

    for rx, ry in resources:
        d_me = cheb((sx, sy), (rx, ry))
        d_opp = cheb((ox, oy), (rx, ry))
        contested = 1 if d_opp <= d_me else 0
        # prefer resources closer to us; heavily prefer when we are not behind
        score = (18 - d_me) + (7 - d_opp) - 10 * contested
        # small nudge to favor nearer to center-ish to avoid corner-camping
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(rx - cx) + abs(ry - cy)
        score -= 0.02 * dist_center
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t
    best_move = (0, 0)
    best_val = -10**18

    # choose move that minimizes our distance to target, but if contested, also moves away from opponent slightly
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me_next = cheb((nx, ny), (tx, ty))
        d_opp_next = cheb((nx, ny), (ox, oy))
        # if we are currently behind, we try to improve faster and also keep some separation
        currently_contested = 1 if cheb((sx, sy), (tx, ty)) >= cheb((ox, oy), (tx, ty)) else 0
        val = -d_me_next + (0.08 * d_opp_next if currently_contested else 0.02 * d_opp_next)
        # deterministic tie-break: prefer staying only if it's not worse
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]