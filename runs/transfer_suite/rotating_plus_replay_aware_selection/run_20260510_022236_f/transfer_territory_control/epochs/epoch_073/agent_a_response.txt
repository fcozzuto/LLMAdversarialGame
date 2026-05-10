def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    if not unclaimed:
        return [0, 0]

    dirs8 = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # pick nearby unclaimed candidates deterministically
    cand = []
    for (x, y) in unclaimed:
        if (x, y) in obstacles:
            continue
        d = abs(x - sx) + abs(y - sy)
        if d <= 12:
            cand.append((d, x, y))
    cand.sort()
    if not cand:
        cand = []
        for (x, y) in unclaimed:
            if (x, y) in obstacles: 
                continue
            d = abs(x - sx) + abs(y - sy)
            cand.append((d, x, y))
        cand.sort()
    cand = cand[:24]

    # frontier bias: prefer unclaimed adjacent to our territory
    def frontier_score(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in self_terr:
                    return -6
        return 0

    up = int(observation.get("self_territory_count") or 0)
    op = int(observation.get("opponent_territory_count") or 0)
    we_lead = up >= op

    # objective: approach cell, but if trailing, prioritize cells closer to opponent (to flip later);
    # if leading, prioritize safer cells (farther from opponent).
    best = None
    best_val = None
    for d, x, y in cand:
        dist_to_opp = abs(x - ox) + abs(y - oy)
        val = d + frontier_score(x, y)
        if we_lead:
            val += max(0, 14 - dist_to_opp) * 0.35
        else:
            val -= max(0, dist_to_opp - 6) * 0.15
        if best is None or val < best_val or (val == best_val and (x, y) < (best[0], best[1])):
            best = (x, y)
            best_val = val

    tx, ty = best
    # choose 1-step move that minimizes distance to target (allow diagonal), avoid obstacles
    curd = abs(tx - sx) + abs(ty - sy)
    chosen = (0, 0)
    bestn = None
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not inb(nx, ny):
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        # lexicographic tie-break: deterministic preference ordering
        key = (nd, abs(dx), abs(dy), dx, dy)
        if bestn is None or key < bestn:
            bestn = key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]