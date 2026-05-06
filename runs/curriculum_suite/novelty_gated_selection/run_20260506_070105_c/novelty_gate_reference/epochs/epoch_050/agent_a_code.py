def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best, bestm = 10**9, (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < best:
                best, bestm = d, (dx, dy)
        return [bestm[0], bestm[1]]

    bestv, bestm = 10**18, (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        distopp = abs(nx - ox) + abs(ny - oy)
        best_for_move = 10**18
        for rx, ry in resources:
            ourd = abs(nx - rx) + abs(ny - ry)
            opd = abs(ox - rx) + abs(oy - ry)
            # prefer resources we are relatively closer to; penalize where opponent is already closer
            val = ourd + max(0, opd - ourd) * 3
            # mild incentive to keep distance from opponent while heading to resource
            val -= distopp * 0.35
            if val < best_for_move:
                best_for_move = val
        # tie-break: prefer keeping chebyshev closer to some resource and moving diagonally
        cheb = 0
        for rx, ry in resources:
            dd = max(abs(nx - rx), abs(ny - ry))
            if cheb == 0 or dd < cheb:
                cheb = dd
        key = (best_for_move, cheb, -distopp, -(dx != 0 and dy != 0), -abs(dx) - abs(dy))
        if key < (bestv, 0, 0, 0, 0) or (best_for_move < bestv):
            bestv = best_for_move
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]