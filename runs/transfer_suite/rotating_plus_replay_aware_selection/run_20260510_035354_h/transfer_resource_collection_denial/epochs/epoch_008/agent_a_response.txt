def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        can_win = 1 if myd <= opd else 0
        delay = myd - opd
        # prefer nearer to win; if none, pick smallest delay (deny indirectly)
        key = (can_win, -delay, -myd if can_win else 0, -abs((rx - ox)), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    cur_is_win = man(sx, sy, tx, ty) <= man(ox, oy, tx, ty)

    moves = []
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        can_win = 1 if myd <= opd else 0
        # prioritize improving win chance, then getting closer to target, then not drifting
        dist_score = -myd
        tighten = -abs(nx - tx) - abs(ny - ty)
        # deterministic tie-break: prefer moves with smaller dx,dy lexicographically
        key = (can_win, 1 if (cur_is_win and can_win) else 0, dist_score, tighten, -dx, -dy)
        moves.append((key, [dx, dy]))

    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: t[0], reverse=True)
    return moves[0][1]