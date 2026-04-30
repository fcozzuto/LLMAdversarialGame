def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        # No resources visible: head toward center to reduce opponent advantage
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    def best_target_from(pos):
        px, py = pos
        best = None
        best_val = None
        for rx, ry in resources:
            d1 = dist((px, py), (rx, ry))
            d2 = dist((ox, oy), (rx, ry))
            # Prefer resources that are nearer to us AND farther (or not as near) to opponent
            val = d1 - 0.75 * d2
            # Slightly prefer closer to immediate capture
            val += 0.02 * (d1 * d1)
            if best_val is None or val < best_val:
                best_val = val
                best = (rx, ry)
        return best

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Evaluate each legal step by the best attainable target advantage
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            # If blocked, allow staying instead (engine will keep in place anyway)
            nx, ny = sx, sy
        target = best_target_from((nx, ny))
        if target is None:
            score = 0
        else:
            d_self = dist((nx, ny), target)
            d_opp = dist((ox, oy), target)
            # Primary: improve our capture closeness; Secondary: deny opponent
            score = -(d_self - 0.9 * d_opp)
            # Tiebreak: keep away from opponent when not strongly improving
            score += 0.001 * dist((nx, ny), (ox, oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [nx - sx, ny - sy]

    # If all scores comparable, ensure move is valid integers in {-1,0,1}
    mx, my = best_move
    if mx not in (-1, 0, 1): mx = 0
    if my not in (-1, 0, 1): my = 0
    return [mx, my]