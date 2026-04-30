def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = [0, 0]
    bestv = -10**18

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue

        d_opp = max(abs(nx - ox), abs(ny - oy))
        d_ctr = max(abs(nx - cx), abs(ny - cy))

        if res:
            d_res = min(max(abs(nx - rx), abs(ny - ry)) for rx, ry in res)
            score = d_opp * 5 - d_res * 2 - d_ctr
        else:
            score = d_opp * 5 - d_ctr

        if score > bestv or (score == bestv and (mx, my) < (bestm[0], bestm[1])):
            bestv, bestm = score, [mx, my]

    return bestm