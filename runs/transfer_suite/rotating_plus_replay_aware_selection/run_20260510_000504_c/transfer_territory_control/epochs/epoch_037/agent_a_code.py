def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # Precompute a few nearest targets to keep scoring cheap.
    unclaimed_list = list(unclaimed)
    opp_list = list(opp_terr)
    res_list = list(resources)

    def nearest_dist(points, x, y, cap):
        best = cap
        for px, py in points:
            d = manh(x, y, px, py)
            if d < best:
                best = d
                if best <= 0:
                    break
        return best

    best_unclaimed_from_nei = nearest_dist(unclaimed_list, sx, sy, 30)
    best_opp_from_nei = nearest_dist(opp_list, sx, sy, 30)

    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        # Base preference: resources > flipping opponent > capturing unclaimed > staying in own territory.
        cell_score = 0
        if (nx, ny) in resources:
            cell_score += 100000
        if (nx, ny) in unclaimed:
            cell_score += 3000
        if (nx, ny) in opp_terr:
            cell_score += 9000
        if (nx, ny) in self_terr:
            cell_score += 100

        # Progress / control pressure terms
        if unclaimed_list:
            d_un = nearest_dist(unclaimed_list, nx, ny, 30)
            cell_score += (best_unclaimed_from_nei - d_un) * 120
            cell_score += max(0, 10 - d_un) * 20
        if opp_list:
            d_opp = nearest_dist(opp_list, nx, ny, 30)
            cell_score += (best_opp_from_nei - d_opp) * 55

        # Avoid getting too close to opponent unless we can flip immediately
        d_to_opp = manh(nx, ny, ox, oy)
        if d_to_opp <= 1 and (nx, ny) not in opp_terr:
            cell_score -= 200
        cell_score += d_to_opp * (-8 if (nx, ny) in opp_terr else -2)

        # Deterministic tie-break: fixed dir order already; keep first max.
        if cell_score > best_score:
            best_score = cell_score
            best_move = [dx, dy]

    return best_move