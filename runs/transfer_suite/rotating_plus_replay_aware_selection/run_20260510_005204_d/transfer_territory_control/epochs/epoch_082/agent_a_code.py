def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")
    resources = to_set("resources")

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    order = dirs

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def nbrs4(x, y):
        return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = (-(10**9), [0, 0])
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = 0
        if (nx, ny) in self_terr:
            sc += 2
        if (nx, ny) in opp_terr:
            sc += 6
        if (nx, ny) in resources:
            sc += 3
        if (nx, ny) in unclaimed:
            neigh = nbrs4(nx, ny)
            sc += 1
            if any(t in self_terr for t in neigh):
                sc += 5
            if any(t in opp_terr for t in neigh):
                sc += 4
        sc += 0.01 * md(nx, ny, ox, oy)
        if sc > best[0]:
            best = (sc, [dx, dy])
    return best[1] if best[1] != [0, 0] or inb(sx, sy) else [0, 0]