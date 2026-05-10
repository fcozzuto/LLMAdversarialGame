def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_set = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_set.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, x, y):
        return abs(x - a) + abs(y - b)

    target = None
    cand = list(unclaimed) if unclaimed else []
    if cand:
        target = min(cand, key=lambda c: (man(sx, sy, c[0], c[1]), c[0] + 7 * c[1]))
    else:
        cand = list(opp_set)
        if cand:
            target = min(cand, key=lambda c: (man(sx, sy, c[0], c[1]), -(c[0] + c[1])))
        else:
            target = (w // 2, h // 2)

    tx, ty = target
    best = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # deterministic: engine keeps position on invalid move

        sc = -man(nx, ny, tx, ty)  # greedy toward target
        if (nx, ny) in unclaimed:
            sc += 10000
        if (nx, ny) in opp_set:
            sc += 50000 - man(nx, ny, sx, sy)  # strongly prefer flipping
        # small tie-breaker: prefer moving toward upper-left to be deterministic
        sc += -(nx + 3 * ny) * 0.001

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]