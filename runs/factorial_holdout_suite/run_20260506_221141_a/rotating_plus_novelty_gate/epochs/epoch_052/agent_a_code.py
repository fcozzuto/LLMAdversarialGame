def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < int(w) and 0 <= y < int(h):
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < int(w) and 0 <= y < int(h) and (x, y) not in blocked:
                res.append((x, y))

    def kingd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = int(w) // 2, int(h) // 2

    if res:
        target = min(res, key=lambda r: (kingd(sx, sy, r[0], r[1]), r[0], r[1]))
    else:
        target = (ox, oy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < int(w) and 0 <= ny < int(h)): 
            continue
        if (nx, ny) in blocked:
            continue
        dcur = kingd(sx, sy, target[0], target[1])
        dnew = kingd(nx, ny, target[0], target[1])
        score = (dcur - dnew) * 1000 - dnew
        score += -kingd(nx, ny, target[0], target[1]) * 0  # keep deterministic structure
        score += -kingd(nx, ny, cx, cy) * 0.01
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]