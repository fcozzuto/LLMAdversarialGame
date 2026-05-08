def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cd(x1, y1, x2, y2):
        return abs(x1 - x2) if abs(x1 - x2) > abs(y1 - y2) else max(abs(x1 - x2), abs(y1 - y2))

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = cd(sx, sy, rx, ry)
        op_d = cd(ox, oy, rx, ry)
        # Prefer resources we can reach not later than opponent; then nearest; then tie-break by coords.
        key = (0 if my_d <= op_d else 1, my_d, -op_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = cd(nx, ny, rx, ry)
        d_opp = cd(ox, oy, rx, ry)
        # Prefer reducing our distance; if tied, prefer keeping resource at least as reachable as opponent.
        key = (d_self, 0 if d_self <= d_opp else 1, abs(nx - rx) + abs(ny - ry), rx, ry, dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]