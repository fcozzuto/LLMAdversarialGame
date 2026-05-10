def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    unC = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_center = abs(nx - cx) + abs(ny - cy)

        if (nx, ny) in oppT:
            s = 1_000_000 - d_opp * 200 - d_center
        elif (nx, ny) in unC:
            s = 200_000 - d_opp * 250 - d_center * 2
        elif (nx, ny) in selfT:
            s = 50_000 - d_opp * 150 - d_center
        else:
            s = -d_opp * 80 - d_center * 3

        if d_opp == 0:
            s += 10_000

        if s > best_score:
            best_score = s
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]