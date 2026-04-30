def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((p[0], p[1]))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            rx, ry = r[0], r[1]
            if (rx, ry) not in obs:
                res.append((rx, ry))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    moves = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if inside(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def dist(a, b, c, d):
        ad = a - c
        bd = b - d
        if ad < 0:
            ad = -ad
        if bd < 0:
            bd = -bd
        return ad + bd

    if res:
        best = None
        for dx, dy, nx, ny in moves:
            cur = None
            for rx, ry in res:
                d_self = dist(nx, ny, rx, ry)
                d_opp = dist(ox, oy, rx, ry)
                # Prefer resources we can reach sooner; small bias to reduce our distance.
                score = (d_self - d_opp, d_self, abs((rx - ox)) + abs((ry - oy)), rx, ry)
                if cur is None or score < cur:
                    cur = score
            # Turn it into a move ranking: smaller tuple is better.
            rank = (cur[0], cur[1], cur[2], cur[3], cur[4], dx, dy)
            if best is None or rank < best:
                best = rank
        # Recover dx,dy from best by searching best rank once more deterministically
        for dx, dy, nx, ny in moves:
            cur = None
            for rx, ry in res:
                d_self = dist(nx, ny, rx, ry)
                d_opp = dist(ox, oy, rx, ry)
                score = (d_self - d_opp, d_self, abs((rx - ox)) + abs((ry - oy)), rx, ry)
                if cur is None or score < cur:
                    cur = score
            rank = (cur[0], cur[1], cur[2], cur[3], cur[4], dx, dy)
            if rank == best:
                return [dx, dy]
    # Fallback: go toward center if no resources
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy, nx, ny in moves:
        rank = (dist(nx, ny, cx, cy), dx, dy)
        if best is None or rank < best:
            best = rank
    for dx, dy, nx, ny in moves:
        rank = (dist(nx, ny, cx, cy), dx, dy)
        if rank == best:
            return [dx, dy]
    return [0, 0]