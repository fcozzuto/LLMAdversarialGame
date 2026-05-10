def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []

    obs = set()
    for p in obstacles_list:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Choose a target where we are relatively closer than opponent (deterministic tie-break).
    best_t = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (myd - opd, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    # Preferred move: step toward target.
    sdx = 0 if rx == sx else (1 if rx > sx else -1)
    sdy = 0 if ry == sy else (1 if ry > sy else -1)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, rx, ry)
        opd2 = cheb(ox, oy, rx, ry)  # opponent assumed to act next; keep consistent
        candidates.append(((myd2 - opd2, myd2, dx, dy), [dx, dy]))
    if not candidates:
        return [0, 0]

    # If preferred move is valid, keep it; otherwise pick best deterministic candidate.
    for k, mv in candidates:
        if mv[0] == sdx and mv[1] == sdy:
            return mv
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]