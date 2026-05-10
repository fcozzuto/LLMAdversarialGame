def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    self_territory = set(tuple(p) for p in (observation.get("self_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_territory = set(tuple(p) for p in (observation.get("opponent_territory", []) or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = [(p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []) if isinstance(p, (list, tuple)) and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    opp_list = list(opp_territory)
    if unclaimed:
        best = None
        bestv = -10**18
        for tx, ty in unclaimed:
            if not inb(tx, ty) or (tx, ty) in obstacles:
                continue
            ds = man(sx, sy, tx, ty)
            do = 10**6
            for px, py in opp_list:
                d = man(px, py, tx, ty)
                if d < do:
                    do = d
                    if do == 0:
                        break
            v = (do - ds) - 0.2 * abs(tx - ox) - 0.1 * abs(ty - oy)
            if v > bestv:
                bestv = v
                best = (tx, ty)
        target = best if best is not None else (sx, sy)
    else:
        target = (sx, sy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestscore = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dcur = man(nx, ny, target[0], target[1])
        dsame = 1 if (nx, ny) in self_territory else 0
        sopp = 1 if (nx, ny) in opp_territory else 0
        doopp = 10**6
        if opp_list:
            for px, py in opp_list:
                d = man(nx, ny, px, py)
                if d < doopp:
                    doopp = d
                    if doopp == 0:
                        break
        score = -dcur + 0.6 * sopp + 0.15 * dsame + 0.05 * doopp
        if score > bestscore:
            bestscore = score
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]