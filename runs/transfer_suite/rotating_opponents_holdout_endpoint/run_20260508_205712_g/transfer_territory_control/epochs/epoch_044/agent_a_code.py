def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = (int(sp[0]), int(sp[1])) if len(sp) >= 2 else (0, 0)
    ox, oy = (int(op[0]), int(op[1])) if len(op) >= 2 else (0, 0)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            try:
                obstacles.add((int(p[0]), int(p[1])))
            except:
                pass

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))
    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))
    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0
        if (x, y) in opp_terr:
            s += 50
        if (x, y) in unclaimed:
            s += 10
        if (x, y) in self_terr:
            s += 1
        dx = x - ox
        dy = y - oy
        dist2 = dx * dx + dy * dy
        s += -dist2 * 0.01
        if abs(dx) + abs(dy) == 0:
            s += 5
        return s

    best = None
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sc = cell_score(nx, ny)
        if sc > best_s:
            best_s = sc
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best