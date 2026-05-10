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

    resset = set()
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            res.append((px, py))
            resset.add((px, py))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def mche(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        ay = b - d
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not res:
        # If no visible resources, try to approach opponent-remote center while avoiding obstacles.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            v = -(mche(nx, ny, cx, cy) + mche(nx, ny, ox, oy) * 0.2)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Evaluate one-step outcomes by "who is closer" to each resource; favor stealing races.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in resset:
            v = 10**6  # immediate pick
        else:
            v = -10**12
            for rx, ry in res:
                myd = mche(nx, ny, rx, ry)
                opd = mche(ox, oy, rx, ry)
                # positive means we are closer (good); negative means opponent likely wins this race
                race = opd - myd
                # Break ties by preferring closer absolute distance (helps when races are similar)
                vcur = race * 100 - myd
                if vcur > v:
                    v = vcur
        # Tiny deterministic bias toward reducing distance to opponent to prevent being pinned
        v -= mche(nx, ny, ox, oy) * 0.01
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best