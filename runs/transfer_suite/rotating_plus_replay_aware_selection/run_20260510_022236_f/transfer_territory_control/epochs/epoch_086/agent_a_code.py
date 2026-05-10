def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def manh(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def closest_dist(x, y, cells):
        if not cells: return 10**9
        best = 10**9
        for (cx, cy) in cells[:64]:
            d = manh(x, y, cx, cy)
            if d < best:
                best = d
                if best == 0: break
        return best

    up = int(observation.get("self_territory_count") or 0)
    op = int(observation.get("opponent_territory_count") or 0)
    we_lead = up >= op

    targets = unclaimed if we_lead else (unclaimed if unclaimed else list(op_terr))
    center = (w // 2, h // 2)

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            sc = -10**12
        else:
            cell_type = 0
            if (nx, ny) in self_terr: cell_type = 1
            elif (nx, ny) in op_terr: cell_type = 3
            else: cell_type = 2  # unclaimed
            dist_t = closest_dist(nx, ny, targets)
            dist_c = manh(nx, ny, center[0], center[1])
            lead_bonus = 0.6 if we_lead and cell_type >= 2 else 0.0
            flip_bonus = 1.2 if (not we_lead and (nx, ny) in op_terr) else 0.0
            sc = cell_type * 10 - dist_t * 1.2 - dist_c * 0.12 + lead_bonus + flip_bonus
        tie = (0 if dx == 0 and dy == 0 else 1)  # avoid staying unless best
        key = (sc, -tie, -(dx * dx + dy * dy), dx, dy)
        if key > best:
            best = key
    return [int(best[3]), int(best[4])]