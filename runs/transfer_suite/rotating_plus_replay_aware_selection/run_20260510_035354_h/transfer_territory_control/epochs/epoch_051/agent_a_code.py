def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    self_cnt = len(self_terr) if isinstance(self_terr, list) else 0
    opp_cnt = len(opp_terr) if isinstance(opp_terr, list) else 0
    aggressive = self_cnt < opp_cnt

    unclaimed = observation.get("unclaimed_cells") or []
    candidates = []
    if not aggressive:
        for p in unclaimed:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                candidates.append((p[0], p[1]))
    if aggressive or not candidates:
        candidates = [(ox, oy)]

    tx, ty = sorted(candidates)[0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestd = None

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        d = man(nx, ny, tx, ty)
        key = (d, abs(dx) + abs(dy), dx, dy)
        if best is None or key < best:
            best = key
            bestd = (dx, dy)

    if bestd is not None:
        return [bestd[0], bestd[1]]

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if 0 <= nx < w and 0 <= ny < h:
            return [dx, dy]
    return [0, 0]