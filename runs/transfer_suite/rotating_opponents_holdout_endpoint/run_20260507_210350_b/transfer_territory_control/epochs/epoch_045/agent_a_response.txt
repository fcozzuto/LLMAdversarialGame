def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def to_set(lst):
        s = set()
        for p in (lst or []):
            if p and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    self_terr = to_set(observation.get("self_territory"))
    opp_terr = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    opp_pos = observation.get("opponent_position") or [None, None]
    ox = int(opp_pos[0]) if opp_pos[0] is not None else None
    oy = int(opp_pos[1]) if opp_pos[1] is not None else None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        sc = 0.0
        if (x, y) in self_terr:
            sc += 0.05
        elif (x, y) in unclaimed:
            sc += 2.2 + 0.15 * edge_dist(x, y)
        elif (x, y) in opp_terr:
            sc += 3.1 + 0.2 * edge_dist(x, y)
        else:
            sc += 0.2 * edge_dist(x, y)
        if ox is not None and oy is not None:
            dist_opp = abs(x - ox) + abs(y - oy)
            sc -= 0.03 * (8 - min(8, dist_opp))
        for ax, ay in dirs:
            nx, ny = x + ax, y + ay
            if inb(nx, ny) and (nx, ny) in obstacles:
                sc -= 0.06
        return sc

    best_dx, best_dy, best_sc = 0, 0, -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_cell(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]