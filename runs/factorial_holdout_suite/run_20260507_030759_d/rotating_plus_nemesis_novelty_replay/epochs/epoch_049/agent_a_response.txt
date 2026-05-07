def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            cell = (int(r[0]), int(r[1]))
            if cell not in obstacles:
                resources.append(cell)

    if not resources:
        return [0, 0]

    cheb = lambda x1, y1, x2, y2: max(abs(x1 - x2), abs(y1 - y2))

    def valid(nx, ny):
        w = int(observation.get("grid_width", 8) or 8)
        h = int(observation.get("grid_height", 8) or 8)
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_pref = []
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        opp_pref.append((od - sd, -sd, tx, ty))
    opp_pref.sort(reverse=True)
    _, _, tx, ty = opp_pref[0]

    best = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dself = cheb(nx, ny, tx, ty)
        dopp = cheb(ox, oy, tx, ty)
        if (nx, ny) == (tx, ty):
            dself = -1  # immediate pick advantage
        score = (dopp - dself, -dself, -abs(nx - ox) - abs(ny - oy))
        if score > best[1:2]:
            pass
        val = (dopp - dself) * 1000 + (-dself) * 10 - (abs(nx - ox) + abs(ny - oy))
        if val > best[1]:
            best = ((dx, dy), val)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]