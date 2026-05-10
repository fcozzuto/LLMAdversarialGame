def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_frontier = set()
    if unclaimed and opp_terr:
        for c in unclaimed:
            cx, cy = c
            for dx, dy in neigh:
                if (cx + dx, cy + dy) in opp_terr:
                    opp_frontier.add(c)
                    break

    targets = list(opp_frontier) if opp_frontier else []
    if not targets:
        targets = [(ox, oy)]

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0
        if (x, y) in opp_terr:
            s += 2000
        if (x, y) in self_terr:
            s -= 5
        best_m = 10**9
        best_near_opp = False
        best_unclaimed = (x, y) in unclaimed
        for tx, ty in targets:
            m = abs(tx - x) + abs(ty - y)
            if m < best_m:
                best_m = m
            if not best_near_opp and best_unclaimed:
                for dx, dy in neigh:
                    if (x + dx, y + dy) in opp_terr:
                        best_near_opp = True
                        break
        s += (200 - best_m)
        if best_near_opp:
            s += 120
        return s

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_cell(nx, ny)
        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score, best_move = sc, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]