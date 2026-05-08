def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    best_move = [0, 0]

    for dx1, dy1 in dirs:
        nx, ny = sx + dx1, sy + dy1
        if not inb(nx, ny):
            continue
        if nx == ox and ny == oy:
            return [dx1, dy1]

        # opponent response: move to maximize distance from our next position
        opp_best_d2 = -1
        for dx2, dy2 in dirs:
            mx, my = ox + dx2, oy + dy2
            if not inb(mx, my):
                mx, my = ox, oy
            d = dist2(nx, ny, mx, my)
            if d > opp_best_d2:
                opp_best_d2 = d

        # maximize: closer now, and make it harder for opponent to keep distance
        d_now = dist2(nx, ny, ox, oy)
        score = (-d_now) + 0.15 * opp_best_d2

        # deterministic tie-break: prefer moves with smaller distance now, then lexicographic dx,dy
        cand = (score, -d_now, dx1, dy1)
        if best is None or cand > best:
            best = cand
            best_move = [dx1, dy1]

    return best_move