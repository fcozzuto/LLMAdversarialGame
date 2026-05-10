def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_cells = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_cells = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    neigh_dirs = dirs  # 8-neighborhood
    bestv = -10**18
    best = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        v = 0
        in_opp = (nx, ny) in opp_cells
        in_self = (nx, ny) in self_cells
        in_unc = (nx, ny) in unclaimed

        if in_opp:
            v += 85
        elif in_self:
            v += 6
        elif in_unc:
            v += 40
        else:
            v += 5

        adj_opp = 0
        for ax, ay in neigh_dirs:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in opp_cells:
                adj_opp += 1

        if in_unc:
            v += 35 * adj_opp
        elif in_self:
            v += 10 * adj_opp
        elif in_opp:
            v += 5 * adj_opp

        d_opp = abs(nx - ox) + abs(ny - oy)
        v += 0.5 * d_opp  # stay farther to reduce immediate counter-flips

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]