def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_list = list(opp_terr) if opp_terr else []
    nearest_opp = None
    if opp_list:
        nearest_opp = min(opp_list, key=lambda p: dist((sx, sy), p))

    def cell_value(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) in opp_terr:
            v = 9.0
        elif (nx, ny) in unclaimed:
            v = 4.3
        elif (nx, ny) in self_terr:
            v = 1.0
        else:
            v = 0.6
        if (nx, ny) in resources:
            v += 2.2
        if nearest_opp is not None:
            d_now = dist((sx, sy), nearest_opp)
            d_new = dist((nx, ny), nearest_opp)
            v += 0.9 * (d_now - d_new)
        v += 0.05 * (w - 1 - abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0))
        return v

    best = (None, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            v = cell_value(nx, ny)
            if v > best[1]:
                best = ((dx, dy), v)
    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]