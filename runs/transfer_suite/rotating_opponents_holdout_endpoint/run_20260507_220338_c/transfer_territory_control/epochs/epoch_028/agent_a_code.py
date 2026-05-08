def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    ox, oy = int(ox), int(oy)

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass

    un_list = observation.get("unclaimed_cells") or []
    unclaimed = set()
    for p in un_list:
        try:
            x, y = p
            unclaimed.add((int(x), int(y)))
        except:
            pass

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = -10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        score = -d
        if (nx, ny) in unclaimed:
            score += 5
        myc = observation.get("self_territory") or []
        myset = observation.get("self_territory_set")
        if myset is None and myc:
            try:
                myset = set((int(a), int(b)) for a, b in myc)
            except:
                myset = set()
        else:
            myset = myset or set()
        if (nx, ny) in myset:
            score += 2
        if dx == 0 and dy == 0:
            score -= 0.5
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best