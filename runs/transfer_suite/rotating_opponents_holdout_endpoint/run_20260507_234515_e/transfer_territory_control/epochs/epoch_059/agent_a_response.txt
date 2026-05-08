def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))
    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))
    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(ox), int(oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0
        if (x, y) in self_terr:
            s += 6
        if (x, y) in unclaimed:
            s += 18
        if (x, y) in opp_terr:
            s += 10  # entering flips on entry; still prefer unclaimed
        # steer away from opponent: avoid giving them easy counterclaim paths
        d_opp = abs(x - ox) + abs(y - oy)
        s += min(10, d_opp) * 0.4
        # mild center preference to prevent being boxed in by counterclaims
        s += (10 - (abs(x - cx) + abs(y - cy))) * 0.05
        return s

    best = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_cell(nx, ny)
        if sc > best:
            best = sc
            best_move = [dx, dy]
    return best_move