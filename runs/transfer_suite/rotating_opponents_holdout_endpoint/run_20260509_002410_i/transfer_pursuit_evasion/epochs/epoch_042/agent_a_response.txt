def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    is_evader = (self_role == "evader") or ("evader" in self_role) or (opponent_role == "pursuer")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy
    def blocked(x, y): return (x, y) in obstacles
    def mobility(x, y):
        m = 0
        for ax, ay in deltas:
            nx, ny = x + ax, y + ay
            if inb(nx, ny) and not blocked(nx, ny):
                m += 1
        return m

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        m = mobility(nx, ny)
        near_corner = (nx == 0 or nx == w - 1) and (ny == 0 or ny == h - 1)
        if is_evader:
            score = (d, m, -1 if near_corner else 0)
            if best is None or score > best_score:
                best, best_score = (dx, dy), score
        else:
            # Pursuer: minimize distance; tie-break by keeping good mobility and reducing opponent escape
            opp_m = mobility(ox, oy)
            score = (-d, m, opp_m)
            if best is None or score > best_score:
                best, best_score = (dx, dy), score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]