def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p is not None and len(p) == 2:
            unclaimed.append((int(p[0]), int(p[1])))
    unclaimed_set = set(unclaimed)

    self_t = set()
    for p in (observation.get("self_territory") or []):
        if p is not None and len(p) == 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in (observation.get("opponent_territory") or []):
        if p is not None and len(p) == 2:
            opp_t.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_list = list(opp_t)
    un_list = unclaimed if unclaimed else list(unclaimed_set)
    if not un_list:
        # fallback targets: cells adjacent to opponent territory that aren't obstacles
        adj = set()
        for (x, y) in opp_t:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in self_t and (nx, ny) not in opp_t:
                    adj.add((nx, ny))
        un_list = list(adj) if adj else [(sx, sy)]

    def min_dist(pt, targets):
        x, y = pt
        best = None
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if best is None or d < best:
                best = d
                if best == 0:
                    return 0
        return best if best is not None else 0

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**9
        else:
            val = 0
            if (nx, ny) in unclaimed_set:
                val += 6
            if (nx, ny) in opp_t:
                val += 3
            if (nx, ny) in self_t:
                val += 1
            du = min_dist((nx, ny), un_list)
            val += -0.9 * du
            if opp_list:
                do = min_dist((nx, ny), opp_list)
                val += -0.2 * do
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            if [dx, dy] < best_move:
                best_move = [dx, dy]
    return best_move