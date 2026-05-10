def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    opp_pos = tuple(observation["opponent_position"])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_boundary = set()
    if opp_terr:
        for (x, y) in opp_terr:
            for dx, dy in dirs8 + [(0, 0)]:
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    opp_boundary.add((nx, ny))

    best_target = None
    if unclaimed and opp_boundary:
        cand = [c for c in unclaimed if tuple(c) in opp_boundary]
        if cand:
            best_target = min(cand, key=lambda c: (man((sx, sy), tuple(c)), man(tuple(opp_pos), tuple(c))))
    if best_target is None:
        if unclaimed:
            best_target = min(unclaimed, key=lambda c: (man((sx, sy), tuple(c))))
            best_target = tuple(best_target)
        else:
            if opp_boundary:
                # prioritize stealing by stepping adjacent to opponent control
                adj = [p for p in opp_boundary if p not in self_terr]
                best_target = min(adj, key=lambda p: man((sx, sy), p)) if adj else tuple(opp_pos)
            else:
                best_target = tuple(opp_pos)

    tx, ty = best_target
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**17
        else:
            cell = (nx, ny)
            val = -man((nx, ny), (tx, ty))
            if cell in unclaimed:
                val += 6.0
            if cell in opp_terr:
                val += 3.6
            if cell in self_terr:
                val += 0.6
            if cell == (sx, sy):
                val -= 0.2
            # slight preference to approach opponent even if target is stale
            val += 0.15 * (man((sx, sy), (opp_pos[0], opp_pos[1])) - man((nx, ny), (opp_pos[0], opp_pos[1])))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]