def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(obj):
        s = set()
        for c in obj or []:
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                s.add((int(c[0]), int(c[1])))
        return s

    un = to_set(observation.get("unclaimed_cells"))
    myt = to_set(observation.get("self_territory"))
    opt = to_set(observation.get("opponent_territory"))
    obst = to_set(observation.get("obstacles"))

    adj4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_adj_to_opt(x, y):
        for dx, dy in adj4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opt:
                return True
        return False

    def closest_dist(px, py, targets):
        best = 10**9
        for tx, ty in targets:
            d = abs(tx - px) + abs(ty - py)
            if d < best:
                best = d
        return best if targets else best

    targets = []
    if un and opt:
        for (x, y) in un:
            if cell_adj_to_opt(x, y):
                targets.append((x, y))
    if not targets:
        targets = list(un) if un else list(opt)

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            if (nx, ny) in obst:
                cand.append((-(10**9), dx, dy))
                continue

            score = 0
            if (nx, ny) in opt:
                score += 260  # direct capture (flip on entry)
            elif (nx, ny) in un:
                score += 120
                if cell_adj_to_opt(nx, ny):
                    score += 80  # edge-blocking / contesting
                # slight preference to expand away from opponent proximity
                score += 20 - (abs(nx - ox) + abs(ny - oy))
                score += 5 * sum(1 for ddx, ddy in adj4 if (nx + ddx, ny + ddy) in myt)
            elif (nx, ny) in myt:
                score += 35  # consolidation

            # distance-to-best contested / unclaimed objective
            score += 30 - closest_dist(nx, ny, targets)
            cand.append((score, dx, dy))

    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = cand[0]
    return [int(dx), int(dy)]