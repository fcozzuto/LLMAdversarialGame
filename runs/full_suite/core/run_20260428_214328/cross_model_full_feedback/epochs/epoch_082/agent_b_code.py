def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    # remove duplicates while preserving order
    seen = set()
    uniq_resources = []
    for r in resources:
        if r not in seen:
            uniq_resources.append(r)
            seen.add(r)
    resources = uniq_resources

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Simple deterministic heuristic: move toward a resource that is relatively closer to us than to opponent
    best = None
    best_score = None
    for r in resources:
        d = cheb((sx, sy), r)
        od = cheb((ox, oy), r)
        score = (od - d) * 10 - d  # prefer resources closer to us and far from opponent
        if best_score is None or score > best_score or (score == best_score and r < best):
            best_score = score
            best = r

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]
    if best is not None:
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            return [dx, dy]

    # Fallback: move to reduce distance to resource if any, else approach center avoiding obstacles
    center = (w // 2, h // 2)
    # choose best move toward center or away from opponent if blocked
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        dist_center = cheb((nx, ny), center)
        dist_opp = cheb((nx, ny), (ox, oy))
        score = -dist_center - dist_opp
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]