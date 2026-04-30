def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort(key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))  # deterministic preference

    if resources:
        best_r = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
        best_od = min(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]), r[0], r[1]))
    else:
        best_r = (w // 2, h // 2)
        best_od = (w // 2, h // 2)

    bestd = cheb(sx, sy, best_r[0], best_r[1])
    oppd = cheb(ox, oy, best_r[0], best_r[1])
    threat = (oppd <= bestd)  # if opponent is at least as close, try to deny

    # Score moves: advance toward best resource; if threat, move toward a resource that is close to opponent too.
    best_target = None
    if resources and threat:
        best_target = min(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]), cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    else:
        best_target = best_r

    cx, cy = sx, sy
    best_score = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = cx + dx, cy + dy
        if not valid(nx, ny):
            continue
        d_to_target = cheb(nx, ny, best_target[0], best_target[1])
        d_to_center = cheb(nx, ny, w // 2, h // 2)
        d_opp_to_target = cheb(ox, oy, best_target[0], best_target[1])
        deny = 0.0
        if threat:
            # reduce opponent advantage if they chase the same target
            deny = 0.7 * (d_opp_to_target - cheb(nx, ny, best_target[0], best_target[1]))
        # Prefer capturing (closer), then staying away from obstacles already implicit, and mild center bias
        score = (-d_to_target) + 0.05 * (-d_to_center) + deny
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]