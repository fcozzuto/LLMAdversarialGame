def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    occ = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                occ.add((px, py))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in occ:
                resources.append((rx, ry))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score_to(tx, ty):
        return abs(tx - ox) + abs(ty - oy)

    if resources:
        resources.sort(key=lambda r: (abs(r[0] - x) + abs(r[1] - y), r[0], r[1]))
        tx, ty = resources[0]
        best = (0, 0)
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ:
                d_self = abs(nx - tx) + abs(ny - ty)
                v = -d_self * 1000 + score_to(nx, ny)
                if v > bestv:
                    bestv, best = v, (dx, dy)
        return [int(best[0]), int(best[1])]

    best = (0, 0)
    bestv = -10**9
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ:
            d_opp = abs(nx - ox) + abs(ny - oy)
            d_self = abs(nx - x) + abs(ny - y)
            v = -d_opp * 1000 - d_self
            if v > bestv:
                bestv, best = v, (dx, dy)
    return [int(best[0]), int(best[1])]