def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_ter = set(map(tuple, observation.get("self_territory") or []))
    opp_ter = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    un_list = list(unclaimed)
    if not un_list:
        return [0, 0]

    def best_un_dist(x, y, limit=6):
        md = 10**9
        # small deterministic scan: prefer nearby targets
        for (tx, ty) in un_list:
            d = man(x, y, tx, ty)
            if d < md:
                md = d
                if md <= limit:
                    break
        return md

    def frontier_bonus(x, y):
        # encourage moves that touch opponent territory or open space
        b = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                if (nx, ny) in unclaimed:
                    b += 1
                elif (nx, ny) in opp_ter:
                    b += 2
        return b

    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in self_ter:
            score += 6
        elif (nx, ny) in unclaimed:
            score += 14
        elif (nx, ny) in opp_ter:
            score += 10  # likely to flip into our territory

        score += 2 * frontier_bonus(nx, ny)

        # push toward unclaimed while reducing distance to opponent (for pressure)
        score += 4.0 * (6 - min(best_un_dist(nx, ny), 6)) / 6.0
        score += 1.5 * (6 - man(nx, ny, ox, oy) if man(nx, ny, ox, oy) <= 6 else 0) / 6.0

        # discourage staying if a better unclaimed cell exists nearby
        score += -0.25 if dx == 0 and dy == 0 else 0

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]