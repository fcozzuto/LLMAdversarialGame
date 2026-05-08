def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (w - 1, h - 1)))

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    opp_list = list(opp_terr)
    if opp_list:
        # Precompute nearest opponent-territory distance for each candidate cell.
        def min_opp_dist(x, y):
            best = 10**9
            for ax, ay in opp_list:
                d = abs(x - ax) + abs(y - ay)
                if d < best:
                    best = d
                    if best == 0:
                        break
            return best
    else:
        def min_opp_dist(x, y):
            return abs(x - ox) + abs(y - oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in resources:
            score += 20
        if (nx, ny) in opp_terr:
            score += 45
        elif (nx, ny) in unclaimed:
            score += 10
        elif (nx, ny) in self_terr:
            score += 2

        dopp = min_opp_dist(nx, ny)
        score -= 3 * dopp  # push toward opponent territory/edges

        adj_unclaimed = 0
        adj_opp = 0
        for ddx, ddy in dirs4:
            ax, ay = nx + ddx, ny + ddy
            if not inb(ax, ay) or (ax, ay) in obstacles:
                continue
            if (ax, ay) in unclaimed:
                adj_unclaimed += 1
            if (ax, ay) in opp_terr:
                adj_opp += 1
        score += 6 * adj_opp
        score += 2 * adj_unclaimed

        # Prefer movement over staying when scores tie.
        score += 1 if (dx != 0 or dy != 0) else 0

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best