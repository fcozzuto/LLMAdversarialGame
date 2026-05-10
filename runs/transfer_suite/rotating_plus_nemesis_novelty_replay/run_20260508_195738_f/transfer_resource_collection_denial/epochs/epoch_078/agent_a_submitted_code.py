def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(a, b, c, d):
        t = a - c
        if t < 0: t = -t
        u = b - d
        if u < 0: u = -u
        return t + u
    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny): continue
                v = -md(nx, ny, ox, oy)
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best
    best_move = [0, 0]
    best_val = -10**18
    # target: resource where we are closer than opponent; else nearest to us
    tar = None
    tar_d = 10**9
    tar_adv = -10**9
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        if ds < do and (do - ds) > tar_adv:
            tar_adv = do - ds
            tar = (rx, ry)
        if tar is None and ds < tar_d:
            tar_d = ds
            tar = (rx, ry)
    rx, ry = tar
    # also consider stealing: choose up to two best resources for maximizing margin
    cand_resources = [(rx, ry)]
    for rx2, ry2 in resources:
        if (rx2, ry2) == (rx, ry): continue
        ds = md(sx, sy, rx2, ry2)
        do = md(ox, oy, rx2, ry2)
        if ds < do:
            cand_resources.append((rx2, ry2))
            if len(cand_resources) >= 3: break
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            # value: get closer to some target while not letting opponent get much closer
            v = 0
            for tx, ty in cand_resources:
                d_self = md(nx, ny, tx, ty)
                d_opp = md(ox, oy, tx, ty)
                v += (d_opp - d_self) * 10 - d_self
            # small repulsion from opponent to reduce immediate contest advantage
            v += -md(nx, ny, ox, oy)
            # prefer moving onto a resource if reachable
            if (nx, ny) in obstacles:
                v -= 10**9
            if (nx, ny) in set(resources):
                v += 10**6
            if v > best_val:
                best_val = v
                best_move = [dx, dy]
    if best_move == [0, 0]:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    best_move = [dx, dy]
                    return best_move
    return best_move