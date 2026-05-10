def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    opp_list = list(opp_terr) if opp_terr else [(int(ox), int(oy))]

    def adj_count(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    def min_dist_to_opp(x, y):
        best = 10**9
        for px, py in opp_list:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
        return best

    best_move = [0, 0]
    best_score = -1e18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in opp_terr:
            score += 120.0 + 12.0 * adj_count(nx, ny, opp_terr) + 3.0 * adj_count(nx, ny, self_terr)
        elif (nx, ny) in self_terr:
            score += 6.0 + 1.5 * adj_count(nx, ny, self_terr)
        elif (nx, ny) in unclaimed:
            score += 18.0 + 7.0 * adj_count(nx, ny, opp_terr) + 2.0 * adj_count(nx, ny, self_terr)
        else:
            score += 3.0 * adj_count(nx, ny, self_terr)

        score += -1.2 * min_dist_to_opp(nx, ny)

        if dx == 0 and dy == 0:
            score -= 1.0  # prefer moving unless equal

        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move