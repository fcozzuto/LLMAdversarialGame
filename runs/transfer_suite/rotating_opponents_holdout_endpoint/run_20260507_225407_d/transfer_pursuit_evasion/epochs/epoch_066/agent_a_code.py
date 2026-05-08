def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res_list = observation.get("resources") or observation.get("resource_positions") or []
    resources = []
    for p in res_list:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def best_res_dist2(x, y):
        if not resources:
            return 10**9
        bd = 10**18
        for rx, ry in resources:
            d = dist2(x, y, rx, ry)
            if d < bd:
                bd = d
        return bd

    best = None
    best_score = -10**30
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dfo = dist2(nx, ny, ox, oy)
        dr = best_res_dist2(nx, ny)
        score = dfo * 2 - dr
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]