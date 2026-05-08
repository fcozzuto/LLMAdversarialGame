def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    resources = set((int(p[0]), int(p[1])) for p in (observation.get("resources") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opp_dist = lambda x, y: abs(x - ox) + abs(y - oy)

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0
        if (x, y) in resources:
            s += 50
        if (x, y) in opp_terr:
            s += 220
            s -= 0.5 * opp_dist(x, y)
        elif (x, y) in unclaimed or ((x, y) not in self_terr and (x, y) not in opp_terr):
            s += 120
            s += 1.2 * (max(0, 7 - opp_dist(x, y)))  # nearer to opponent is better
            # Prefer cutting through opponent's boundary (adjacent to opponent cells)
            adj_opp = 0
            for dx, dy in neigh:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in opp_terr:
                    adj_opp += 1
            s += 25 * adj_opp
        else:  # in self territory
            s += 10
            # Encourage expansion from frontier (adjacent unclaimed/opponent)
            adj_empty = 0
            adj_opp = 0
            for dx, dy in neigh:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in self_terr:
                    if (nx, ny) in opp_terr:
                        adj_opp += 1
                    else:
                        adj_empty += 1
            s += 8 * adj_empty + 18 * adj_opp
        # Mild obstacle avoidance
        adj_ob = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in obstacles:
                adj_ob += 1
        s -= 3 * adj_ob
        return s

    best = None
    best_move = [0, 0]
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        s = score_cell(nx, ny)
        key = (s, -opp_dist(nx, ny), -abs(nx - sx) - abs(ny - sy), dx, dy)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]
    return best_move