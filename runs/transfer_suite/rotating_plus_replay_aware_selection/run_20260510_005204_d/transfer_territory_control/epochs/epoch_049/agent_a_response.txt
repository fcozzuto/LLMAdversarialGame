def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_unclaimed_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                c += 1
        return c

    def adj_opp_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in opp_terr:
                c += 1
        return c

    def score(nx, ny):
        s = 0.0
        s += 0.75 * (-(abs(nx - cx) + abs(ny - cy)))  # drift toward center (denser territory)
        if (nx, ny) in unclaimed:
            s += 6.0 + 1.2 * adj_unclaimed_count(nx, ny)
            s += 0.8 * adj_opp_count(nx, ny)  # contention creates momentum against sweeper
        if (nx, ny) in opp_terr:
            s += 10.0 + 0.9 * adj_unclaimed_count(nx, ny) + 0.5 * adj_opp_count(nx, ny)
        if (nx, ny) in self_terr:
            s += 1.0  # keep coherence; avoids unnecessary flips when not beneficial
        if (nx, ny) in self_terr and (nx != sx or ny != sy):
            s -= 0.2  # slightly discourage wandering inside our territory
        return s

    best_move = (0, 0)
    best_score = -1e18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]