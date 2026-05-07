def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    for (rx, ry) in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        lead = opd - myd  # positive means I arrive first
        # prefer positive lead; if tie, shorter my distance; then determinism by coords
        key = (lead, -myd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))

    (_, (tx, ty)) = best

    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # If direct target step is blocked, try alternative neighbor steps deterministically
    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for nx, ny in neigh:
        ax, ay = sx + nx, sy + ny
        if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
            cand.append((nx, ny, dist(ax, ay, tx, ty)))
    if not cand:
        return [0, 0]

    # choose move that minimizes distance to target; tie by deterministic order already in neigh
    cand.sort(key=lambda t: (t[2], neigh.index((t[0], t[1]))))
    return [int(cand[0][0]), int(cand[0][1])]