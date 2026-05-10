def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for c in observation.get("obstacles") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obst.add((int(c[0]), int(c[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inside(x, y)) or ((x, y) in obst)

    self_cells = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_cells.add((int(p[0]), int(p[1])))
    opp_cells = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_cells.add((int(p[0]), int(p[1])))

    unclaimed = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2]
    unclaimed_set = set(unclaimed)

    self_count = int(observation.get("self_territory_count", len(self_cells)) or 0)
    opp_count = int(observation.get("opponent_territory_count", len(opp_cells)) or 0)
    behind = self_count < opp_count

    targets = unclaimed if behind and unclaimed else (list(opp_cells) if opp_cells else (unclaimed if unclaimed else []))
    if not targets:
        targets = [(ox, oy)]

    def dist_to_targets(x, y):
        best = 10**9
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (10**18, None, None)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        gain = 0
        if (nx, ny) in self_cells:
            gain += 1
        elif (nx, ny) in unclaimed_set:
            gain += 3 if behind else 2
        elif (nx, ny) in opp_cells:
            gain += 5 if not behind else 6

        if dx == 0 and dy == 0:
            gain -= 1

        dist = dist_to_targets(nx, ny)
        # maximize gain, then minimize distance; deterministic tie-break by dir order
        key = (-gain, dist)
        if key < (best_move[0], best_move[1] if best_move[1] is not None else (10**9,)):
            best_move = (key[0], key[1], (dx, dy))

    if best_move[2] is None:
        return [0, 0]
    return [int(best_move[2][0]), int(best_move[2][1])]