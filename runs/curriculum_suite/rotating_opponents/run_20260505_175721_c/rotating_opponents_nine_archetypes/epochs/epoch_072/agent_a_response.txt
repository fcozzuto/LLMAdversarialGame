def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            moves.append((dx, dy, nx, ny))

    best = None
    for dx, dy, nx, ny in moves:
        best_res = None
        best_adv = None
        for rx, ry in resources:
            ts = cdist(nx, ny, rx, ry)
            to = cdist(ox, oy, rx, ry)
            # Prefer resources where we are earlier; otherwise still prefer ones that keep opponent slow.
            adv = (to - ts) * 10 - ts
            opp_dist = to
            key = (adv, opp_dist, rx, ry)
            if best_adv is None or key > best_res[0]:
                best_res = (key, (ts, to))
                best_adv = key
        # Tie-break deterministically: prefer smaller ts; then smaller rx+ry; then lexicographic move
        ts, to = best_res[1]
        score_key = (best_res[0][0], -best_res[0][1], -ts, -(nx + ny), dx, dy, nx, ny)
        if best is None or score_key > best[0]:
            best = (score_key, [dx, dy])

    return best[1]