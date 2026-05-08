def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = observation.get("resources") or []
    resources = []
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = moves[0]
    best_score = -10**18

    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_opp = dist2(nx, ny, ox, oy)
        if resources:
            d_res = min(dist2(nx, ny, rx, ry) for rx, ry in resources)
        else:
            d_res = 0
        score = d_opp * 10 - d_res
        if dx == 0 and dy == 0:
            score -= 1
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move