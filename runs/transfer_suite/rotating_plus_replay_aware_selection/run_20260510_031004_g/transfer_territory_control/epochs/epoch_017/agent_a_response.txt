def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    resources = set(map(tuple, observation.get("resources", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    opp_front = set()
    for (x, y) in opp_terr:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in opp_terr:
                    opp_front.add((nx, ny))

    def nearest_dist(cells, x, y):
        d = 10**9
        for cx, cy in cells:
            dd = abs(cx - x) + abs(cy - y)
            if dd < d: d = dd
        return d if d != 10**9 else 9999

    target_un = unclaimed | opp_front
    d_un = nearest_dist(target_un, sx, sy) if target_un else 9999
    d_to_opp = nearest_dist(opp_front, sx, sy) if opp_front else 9999

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0

        if (nx, ny) in opp_terr:
            score += 1200.0
            score += max(0, 18 - man(px, py, nx, ny)) * 4.0
            score -= max(0, 18 - man(sx, sy, nx, ny)) * 0.5
        elif (nx, ny) in unclaimed:
            score += 320.0
            score += max(0, 16 - nearest_dist(unclaimed, nx, ny)) * 6.0
        elif (nx, ny) in opp_front:
            score += 220.0
            score += max(0, 14 - man(nx, ny, px, py)) * 2.0

        if (nx, ny) in self_terr:
            score += 30.0

        if (nx, ny) in resources:
            score += 220.0

        dn = nearest_dist(target_un, nx, ny) if target_un else 9999
        score += max(0, (d_un - dn)) * 10.0

        if opp_front:
            dpf = nearest_dist(opp_front, nx, ny)
            score += max(0, (d_to_opp - dpf)) * 8.0

        # Keep moves that don't help opponent too much
        score -= min(60, man(nx, ny, px, py)) * 0.3

        # Small deterministic tie-break: prefer larger dx/dy lexicographically
        if score > best_score or (score == best_score and (dx, dy) > tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move