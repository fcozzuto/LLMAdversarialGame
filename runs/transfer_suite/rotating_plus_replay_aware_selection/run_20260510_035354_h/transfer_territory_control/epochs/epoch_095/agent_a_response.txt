def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ax, ay = observation.get("self_position", (0, 0))
    bx, by = observation.get("opponent_position", (0, 0))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []

    def toset(lst):
        s = set()
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    uset, oset, ucell, obset = toset(self_terr), toset(opp_terr), toset(unclaimed), toset(obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adjacent_to_set(cell, target_set):
        x, y = cell
        for dx, dy in adj4:
            if (x + dx, y + dy) in target_set:
                return True
        return False

    candidates = []
    if ucell:
        exp = [c for c in ucell if adjacent_to_set(c, uset)]
        if exp:
            candidates = exp
        else:
            blk = [c for c in ucell if adjacent_to_set(c, oset)]
            candidates = blk if blk else list(ucell)
    else:
        candidates = []

    def dist2(p, q):
        dx = p[0] - q[0]
        dy = p[1] - q[1]
        return dx * dx + dy * dy

    target = None
    if candidates:
        candidates.sort(key=lambda c: (dist2((ax, ay), c), abs(c[0] - bx) + abs(c[1] - by), c[0], c[1]))
        target = candidates[0]

    moves = neigh8
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue

        score = 0
        if (nx, ny) in ucell:
            score += 200000
        if (nx, ny) in oset:
            score += 120000

        if target is not None:
            score += -dist2((nx, ny), target)

        # Counterclaim pressure: if opponent is close, prefer moves that reduce distance to opponent territory.
        opp_adj = 0
        for odx, ody in adj4:
            if (nx + odx, ny + ody) in oset:
                opp_adj += 1
        score += 900 * opp_adj

        # Keep from collapsing into tight zones near obstacles.
        obs_near = 0
        for ox, oy in adj4:
            if (nx + ox, ny + oy) in obset:
                obs_near += 1
        score -= 120 * obs_near

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]