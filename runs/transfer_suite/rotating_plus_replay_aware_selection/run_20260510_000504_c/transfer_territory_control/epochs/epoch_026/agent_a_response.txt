def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    self_count = observation.get("self_territory_count", len(self_terr))
    opp_count = observation.get("opponent_territory_count", len(opp_terr))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8(x, y):
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    def adj_count(cell, terr):
        x, y = cell
        c = 0
        for nx, ny in neigh8(x, y):
            if (nx, ny) in terr:
                c += 1
        return c

    # Candidate targets: unclaimed cells, prioritized by adjacency to self/opp frontiers and distance.
    candidates = []
    if unclaimed:
        going_defensive = opp_count > self_count
        for (x, y) in unclaimed:
            if (x, y) in obstacles:
                continue
            a_self = adj_count((x, y), self_terr)
            if a_self == 0 and not going_defensive:
                continue
            a_opp = adj_count((x, y), opp_terr) if going_defensive else adj_count((x, y), opp_terr)
            # Heuristic:
            # - Always prefer cells next to our territory (expand).
            # - If defensive, also prefer cells next to opponent territory (disrupt/limit their spread).
            # - Prefer closer to reduce path uncertainty and claim sooner.
            dist = abs(x - sx) + abs(y - sy)
            if going_defensive:
                score = 60 * a_self + 45 * a_opp - dist
            else:
                score = 70 * a_self + 15 * a_opp - dist
            candidates.append((score, x, y))
    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    tx, ty = candidates[0][1], candidates[0][2]

    # Step toward target with obstacle-avoidance (local).
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer moves that reduce distance to target; tie-break by adjacency gain.
        v = - (abs(tx - nx) + abs(ty - ny))
        v += 2 * adj_count((nx, ny), self_terr)
        if (nx, ny) in opp_terr:
            v += 5  # entering opponent territory flips control
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]