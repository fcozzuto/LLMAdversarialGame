def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles_raw = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obstacles_raw if p is not None)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_set = set(tuple(p) for p in unclaimed if p is not None)

    self_territory = observation.get("self_territory") or []
    self_set = set(tuple(p) for p in self_territory if p is not None)

    opp_territory = observation.get("opponent_territory") or []
    opp_set = set(tuple(p) for p in opp_territory if p is not None)

    resources = observation.get("resources") or []
    res_pts = [tuple(p) for p in resources if p is not None]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = 0
        if (nx, ny) in unclaimed_set:
            v += 4
        if (nx, ny) in opp_set and (nx, ny) not in self_set:
            v += 3
        if (nx, ny) in self_set:
            v -= 1
        v -= manh((nx, ny), (ox, oy))
        if res_pts:
            v -= min(manh((nx, ny), r) for r in res_pts)
        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best