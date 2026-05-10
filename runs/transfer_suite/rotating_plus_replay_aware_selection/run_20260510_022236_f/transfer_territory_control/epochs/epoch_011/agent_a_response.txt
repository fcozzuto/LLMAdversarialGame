def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells") or observation.get("unclaimed") or [])
    self_terr = to_set(observation.get("self_territory"))
    opp_terr = to_set(observation.get("opponent_territory"))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    man = lambda a, b, c, d: abs(a - c) + abs(b - d)

    unclaimed = {(x, y) for (x, y) in unclaimed if inb(x, y) and (x, y) not in obstacles}
    opp_terr_list = [p for p in opp_terr if inb(p[0], p[1])]
    frontier_dist = {}
    if opp_terr_list:
        for (x, y) in unclaimed:
            d = min(man(x, y, px, py) for (px, py) in opp_terr_list)
            frontier_dist[(x, y)] = d

    resources = to_set(observation.get("resources") or [])
    resources = {(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles}

    if resources:
        target = min(resources, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
    elif unclaimed:
        def key(p):
            dself = man(sx, sy, p[0], p[1])
            df = frontier_dist.get(p, 999)
            return (dself - 0.35 * df, df, p[0], p[1])
        target = min(unclaimed, key=key)
    else:
        target = (ox, oy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dtar = man(nx, ny, target[0], target[1])
        # Encourage contesting: being closer to opponent territory if we have a choice.
        if opp_terr_list:
            dopp = min(man(nx, ny, px, py) for (px, py) in opp_terr_list)
        else:
            doup = 999
            dopp = doup
        # Small bias to avoid getting stuck: don't wander if equal.
        dcur_tar = man(sx, sy, target[0], target[1])
        improve = dcur_tar - dtar
        score = (-(improve), dtar, dopp, nx, ny)
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]