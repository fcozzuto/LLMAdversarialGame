def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target choice: prioritize resources we can reach no slower than opponent; otherwise, pick the best compromise.
    best = None
    best_key = None
    t = observation.get("turn_index", 0) or 0
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        ahead = 0 if myd <= opd else 1  # 0 is better (we are not slower)
        # Deterministic tie-break: slight preference based on resource location and turn parity.
        tieb = ((rx * 13 + ry * 7 + t) % 101) / 101.0
        key = (ahead, myd, -opd, tieb)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = [0, 0]
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Prefer reducing our distance; if tied, slow opponent approach a bit and avoid obstacles already handled.
        key = (myd2, -opd2, (nx * 17 + ny * 19 + t) % 97)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = [dx, dy]
    return best_m