def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Choose the resource that I reach best after this move; value = how much closer I am than opponent to that same resource.
        best_r = None
        best_my = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not (0 <= rx < w and 0 <= ry < h):
                continue
            myd = dist(nx, ny, rx, ry)
            if best_my is None or myd < best_my or (myd == best_my and (rx, ry) < best_r):
                best_my = myd
                best_r = (rx, ry)
        rx, ry = best_r
        oppd = dist(ox, oy, rx, ry)
        val = oppd - best_my
        # Prefer higher val; tie-break deterministically by move coordinates.
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]