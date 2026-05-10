def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    sx, sy = int(sx), int(sy)
    ox, oy = observation["opponent_position"]
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for x, y in observation.get("obstacles") or []:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    recent = set()
    path = observation.get("self_path") or []
    for p in path[-8:]:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            recent.add((int(p[0]), int(p[1])))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def adj_score(x, y):
        s = 0
        for dx, dy in dirs[1:]:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            if (nx, ny) in opp_set:
                s += 1.2
            elif (nx, ny) in unclaimed:
                s += 0.7
        return s

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0.0
        if (nx, ny) in opp_set:
            v += 2.6  # flipping pressure
        elif (nx, ny) in unclaimed:
            v += 1.4  # claim expansion
        elif (nx, ny) in self_set:
            v += 0.4  # maintain

        v += 0.35 * adj_score(nx, ny)
        d_self = dist(nx, ny, sx, sy)
        v -= 0.08 * d_self  # avoid pointless moves
        v -= 0.06 * dist(nx, ny, ox, oy)  # avoid being counterclaimed close
        if (nx, ny) in recent and (dx, dy) != (0, 0):
            v -= 0.9  # break loops

        if v > bestv or (v == bestv and (dx, dy) == (0, 0)):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]