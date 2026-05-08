def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target_cells = []
    for c in unclaimed:
        target_cells.append(c)
    for c in opp_set:
        target_cells.append(c)
    if not target_cells:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mindist(x, y, cells, cap=9):
        best = cap
        for cx, cy in cells:
            d = abs(x - cx) + abs(y - cy)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        immediate = 0
        if (nx, ny) in unclaimed:
            immediate += 1
        if (nx, ny) in opp_set:
            immediate += 2
        if (nx, ny) in self_set:
            immediate += 0
        # Prefer moving toward nearest valuable cell, tie-break deterministically.
        d = mindist(nx, ny, target_cells, cap=20)
        key = (-immediate, d, nx, ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]