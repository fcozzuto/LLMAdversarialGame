def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_t = None
    best_key = None
    for tx, ty in resources:
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        key = (od - sd, -sd, -(tx + ty), tx, ty)  # prefer we reach sooner, then closer
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nsd = md(nx, ny, tx, ty)
        # prefer decreasing distance; if tie, prefer not getting closer to opponent's target race
        nkey = (-(nsd), -(md(nx, ny, tx, ty) == 0), (md(ox, oy, tx, ty) - nsd), -abs(tx - nx) - abs(ty - ny), -dx, -dy)
        if best_score is None or nkey > best_score:
            best_score = nkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]