def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
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
    if not resources:
        return [0, 0]

    def best_dist2(x, y):
        m = 10**18
        for rx, ry in resources:
            dx, dy = rx - x, ry - y
            d2 = dx * dx + dy * dy
            if d2 < m:
                m = d2
        return m

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**30
    opp_d2 = (ox - sx) * (ox - sx) + (oy - sy) * (oy - sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d2 = best_dist2(nx, ny)
        nd2o = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        score = -d2
        if nd2o > 0:
            score += min(2000, nd2o // 4)
        if opp_d2 < 9 and nd2o > opp_d2:
            score += 500
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]