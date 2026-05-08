def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    neigh = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    adj_opp = set()
    if opp_t and unclaimed:
        for ux, uy in unclaimed:
            for dx, dy in neigh:
                if (ux + dx, uy + dy) in opp_t:
                    adj_opp.add((ux, uy))
                    break

    cand_targets = list(adj_opp) if adj_opp else list(unclaimed)
    if not cand_targets:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_key = None
    for tx, ty in cand_targets:
        key = (man(ox, oy, tx, ty), man(sx, sy, tx, ty), tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        dcur = man(sx, sy, tx, ty)
        dnew = man(nx, ny, tx, ty)
        gain = 0
        if (nx, ny) in opp_t:
            gain += 5
        elif (nx, ny) in unclaimed:
            gain += 2
        elif (nx, ny) in self_t:
            gain += 0
        # Prefer reducing distance to chosen target; if tie, prefer moves that intersect opponent territory edge.
        val = gain * 100 + (dcur - dnew) * 3 + (-man(nx, ny, ox, oy))
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]