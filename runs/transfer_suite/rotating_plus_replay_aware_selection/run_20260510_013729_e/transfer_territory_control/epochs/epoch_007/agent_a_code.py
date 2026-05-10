def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def adj_to(setter, px, py):
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = px + dx, py + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in setter:
                return True
        return False

    opp_adj = []
    self_adj = []
    for cx, cy in unclaimed:
        if adj_to(opp_ter, cx, cy):
            opp_adj.append((cx, cy))
        elif adj_to(self_ter, cx, cy):
            self_adj.append((cx, cy))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if opp_adj:
        target = min(opp_adj, key=lambda c: (dist((x, y), c), dist((ox, oy), c)))
    elif self_adj:
        target = min(self_adj, key=lambda c: (dist((x, y), c), dist((ox, oy), c)))
    elif unclaimed:
        target = min(unclaimed, key=lambda c: (dist((x, y), c), dist((ox, oy), c)))
    else:
        # If no unclaimed, push toward opponent while avoiding obstacles when possible.
        target = (ox, oy)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cell_value(nx, ny):
        if (nx, ny) in obstacles:
            return -999
        if (nx, ny) in opp_ter:
            return 3
        if (nx, ny) in unclaimed:
            return 2
        if (nx, ny) in self_ter:
            return 1
        return 0

    best = (None, -10**9, 10**9, 10**9)  # move, score, dcur, dopp
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        dcur = abs(nx - target[0]) + abs(ny - target[1])
        dopp = abs(nx - ox) + abs(ny - oy)
        val = cell_value(nx, ny)
        if dx != 0 or dy != 0:
            # Prefer moves that reduce distance to target, but not at the cost of stepping into obstacles.
            val += max(0, 2 - dcur)
        # Tie-break deterministically.
        key = (val, -dopp, -((dx == 0 and dy == 0)), -dcur, dx, dy)
        if key > (best[1], -best[3], -(best[0] == (0, 0) if best[0] is not None else False), -best[2], best[0][0] if best[0] else -2, best[0][1] if best[0] else -2):
            best = ((dx, dy), val, dcur, dopp)

    dx, dy = best[0] if best[0] is not None else (0, 0)
    return [int(dx), int(dy)]