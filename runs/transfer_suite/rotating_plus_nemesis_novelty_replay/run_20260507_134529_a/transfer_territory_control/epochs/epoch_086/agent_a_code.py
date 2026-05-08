def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_to_opp(x, y):
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_terr:
                return True
        return False

    frontier = []
    for cell in unclaimed:
        if adj_to_opp(cell[0], cell[1]):
            frontier.append(cell)

    targets = frontier if frontier else list(unclaimed)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cell_value(nx, ny):
        v = 0.0
        if (nx, ny) in opp_terr:
            v += 10.0
        if (nx, ny) in unclaimed:
            v += 3.0
        if (nx, ny) in self_terr:
            v += 0.5
        if (nx, ny) in resources:
            v += 2.0
        if (nx, ny) in unclaimed and adj_to_opp(nx, ny):
            v += 2.5
        v += -0.35 * (abs(nx - ox) + abs(ny - oy))  # pressure opponent
        return v

    best = (-(10**9), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = cell_value(nx, ny)
        # tie-break deterministically toward reducing distance to nearest target
        if targets:
            dmin = 10**9
            for tx, ty in targets[:8]:
                d = abs(nx - tx) + abs(ny - ty)
                if d < dmin:
                    dmin = d
            v += -0.01 * dmin
        if v > best[0]:
            best = (v, dx, dy)

    if best[0] > -(10**8):
        return [int(best[1]), int(best[2])]
    return [0, 0]