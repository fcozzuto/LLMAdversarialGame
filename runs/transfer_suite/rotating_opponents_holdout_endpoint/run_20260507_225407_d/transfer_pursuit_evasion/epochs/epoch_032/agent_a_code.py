def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def distc(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    scores = observation.get("scores")
    my_score = 0
    opp_score = 0
    if isinstance(scores, dict):
        my_score = scores.get("self", scores.get("me", scores.get("agent", 0)))
        opp_score = scores.get("opponent", scores.get("opp", scores.get("enemy", 0)))
    elif isinstance(scores, (list, tuple)) and len(scores) >= 2:
        my_score, opp_score = scores[0], scores[1]
    else:
        my_score = observation.get("self_score", 0) or 0
        opp_score = observation.get("opponent_score", 0) or 0

    pursuer = my_score <= opp_score

    res = observation.get("resources") or []
    res_pts = []
    for p in res:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                res_pts.append((x, y))
    use_res = len(res_pts) > 0

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if use_res:
            nearest = min(distc(nx, ny, rx, ry) for rx, ry in res_pts)
            val = -nearest
        else:
            d = distc(nx, ny, ox, oy)
            val = -d if pursuer else d
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best