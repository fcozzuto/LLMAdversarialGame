def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    selfT = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    oppT = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                unclaimed.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    target = None
    if unclaimed:
        bestd = 10**18
        for x, y in unclaimed:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd = d
                target = (x, y)
    else:
        target = (ox, oy)

    best_move = (0, 0)
    best_val = -10**18
    tx, ty = target

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if (nx, ny) in selfT:
            cell_gain = 0
        elif (nx, ny) in oppT:
            cell_gain = 7  # flipping into opponent territory
        else:
            cell_gain = 4  # likely unclaimed/neutral

        dist_to_target = abs(tx - nx) + abs(ty - ny)
        dist_to_op = abs(ox - nx) + abs(oy - ny)
        val = 100 * cell_gain - 3 * dist_to_target + 2 * (dist_to_op > 0) * dist_to_op
        if cell_gain >= 4:
            val += 15 - dist_to_target  # prioritize progress when claiming

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]