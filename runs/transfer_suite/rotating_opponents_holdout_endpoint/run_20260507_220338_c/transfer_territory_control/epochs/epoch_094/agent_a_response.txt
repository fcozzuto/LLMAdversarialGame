def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    selfT = set(tuple(t) for t in observation.get("self_territory") or [])
    oppT = set(tuple(t) for t in observation.get("opponent_territory") or [])
    unclaimed = set(tuple(c) for c in observation.get("unclaimed_cells") or [])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def neighbors(x, y):
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inside(nx, ny):
                yield nx, ny

    def pos_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) == (ox, oy):
            return -10**8
        s = 0
        if (nx, ny) in oppT:
            s += 100000
        elif (nx, ny) in unclaimed:
            s += 120
        else:
            s += 10 if (nx, ny) in selfT else 0

        # Expand from frontier: prefer positions adjacent to our territory
        adj_self = 0
        adj_opp = 0
        adj_uncl = 0
        adj_obs = 0
        for ax, ay in neighbors(nx, ny):
            if (ax, ay) in obstacles:
                adj_obs += 1
            elif (ax, ay) in selfT:
                adj_self += 1
            elif (ax, ay) in oppT:
                adj_opp += 1
            elif (ax, ay) in unclaimed:
                adj_uncl += 1
        s += 18 * adj_self
        s += 10 * adj_uncl
        s += 8 * adj_opp

        # Keep some distance from opponent to avoid easy counter-flips
        dist_now = abs(sx - ox) + abs(sy - oy)
        dist_next = abs(nx - ox) + abs(ny - oy)
        s += (dist_next - dist_now) * 2

        # Mild penalty for getting boxed in by obstacles
        s -= adj_obs * 2
        return s

    best = None
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = pos_score(nx, ny)
        if best is None or sc > best_s:
            best_s = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]