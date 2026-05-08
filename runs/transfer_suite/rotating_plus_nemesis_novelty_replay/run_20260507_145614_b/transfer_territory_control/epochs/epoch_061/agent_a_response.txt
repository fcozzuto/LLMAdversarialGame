def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    self_terr = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            self_terr.add((p[0], p[1]))
    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.add((p[0], p[1]))
    opp_terr = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_terr.add((p[0], p[1]))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_opp = man(nx, ny, ox, oy)
        nbrs = 0
        nbr_uncl = 0
        for ax, ay in moves:
            tx, ty = nx + ax, ny + ay
            if (ax, ay) == (0, 0):
                continue
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                nbrs += 1
                if (tx, ty) in unclaimed:
                    nbr_uncl += 1

        if (nx, ny) in self_terr:
            base = 2
        elif (nx, ny) in unclaimed:
            base = 18 + 2 * nbr_uncl
        elif (nx, ny) in opp_terr:
            base = 4 + 1 * nbr_uncl - 0.7 * man(nx, ny, sx, sy) - 6 / (1 + d_opp)
        else:
            base = 6 + 1 * nbr_uncl

        # For a sweeper archetype, avoid getting too close unless we're taking unclaimed.
        risk = 0
        if d_opp <= 1 and (nx, ny) not in unclaimed:
            risk = 12
        if d_opp == 0:
            risk = 20

        # Prefer moves that increase separation while still capturing.
        sep = 0.08 * (d_opp - man(sx, sy, ox, oy))
        score = base + sep - risk + 0.01 * (nbrs - 1)
        key = (score, -dx, -dy, nx, ny)
        if best[0] < key[0]:
            best = (key[0], dx, dy)
    return [int(best[1]), int(best[2])]