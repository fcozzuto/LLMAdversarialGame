def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = observation.get("resources") or []
    cand_targets = []
    for p in resources:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                cand_targets.append((x, y))
        except:
            pass

    if not cand_targets:
        cand_targets = [(ox, oy)]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        t = min(cand_targets, key=lambda p: dist2((nx, ny), p))
        score = dist2((nx, ny), t)
        score += 0 if t != (ox, oy) else dist2((nx, ny), (ox, oy)) * 0
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]