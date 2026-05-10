def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h:
                res.append((rx, ry))
    resset = set(res)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (-1, 0), (1, 0), (0, 1), (0, 0)]

    if res:
        bestt = None
        bestv = -10**18
        for rx, ry in res:
            ds = man(x, y, rx, ry)
            do = man(ox, oy, rx, ry)
            v = (do - ds) * 100 - ds  # prefer resources we can reach sooner
            if v > bestv or (v == bestv and (ds < man(ox, oy, rx, ry))):
                bestv = v
                bestt = (rx, ry)
        tx, ty = bestt
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    bestm = [0, 0]
    bestscore = -10**18
    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            continue
        immediate = 100000 if (nx, ny) in resset else 0
        if res:
            ds2 = man(nx, ny, tx, ty)
            do2 = man(ox, oy, tx, ty)
            s = immediate + (do2 - ds2) * 1000 - ds2
        else:
            s = immediate - man(nx, ny, tx, ty)
        if s > bestscore:
            bestscore = s
            bestm = [dx0, dy0]
    return [int(bestm[0]), int(bestm[1])]