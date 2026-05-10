def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 0, 0

    sp = observation.get("self_position") or (0, 0)
    ap = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    def adj_count(sset, x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in sset:
                c += 1
        return c

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in opp_terr:
            score += 50
        if (nx, ny) in unclaimed:
            score += 30
        if (nx, ny) in self_terr:
            score += 8
        score += 2 * adj_count(unclaimed, nx, ny)
        score += 1 * adj_count(opp_terr, nx, ny)
        score += -abs(nx - ox) - abs(ny - oy)
        if score > best[0]:
            best = (score, dx, dy)

    if best[1] == 0 and best[2] == 0:
        return [0, 0]
    return [int(best[1]), int(best[2])]