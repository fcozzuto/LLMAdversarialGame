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

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # pick target deterministically: prioritize resources where we can arrive no later; otherwise closest race
    best = None
    for rx, ry in resources:
        myd = kdist(sx, sy, rx, ry)
        opd = kdist(ox, oy, rx, ry)
        my_win = 1 if myd <= opd else 0
        # key: win first, then earlier arrival, then tighter race, then closer to center-ish
        cx = rx - (w - 1) / 2.0
        cy = ry - (h - 1) / 2.0
        center_pen = -(cx * cx + cy * cy)
        key = (my_win, -myd, -(myd - opd), center_pen, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry, myd, opd)

    _, tx, ty, _, _ = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd2 = kdist(nx, ny, tx, ty)
        opd2 = kdist(ox, oy, tx, ty)
        # deny: if tie in our progress, prefer increasing opponent's distance; then prefer our being closer
        key = (-myd2, opd2, -abs(tx - nx) - abs(ty - ny))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move