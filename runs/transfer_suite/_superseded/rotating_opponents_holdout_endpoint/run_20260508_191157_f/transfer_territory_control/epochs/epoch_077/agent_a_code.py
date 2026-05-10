def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                unclaimed.append((x, y))

    if unclaimed:
        best = None
        bestv = None
        for x, y in unclaimed:
            dself = abs(x - sx) + abs(y - sy)
            dopp = abs(x - ox) + abs(y - oy)
            v = (dopp - dself, dself, x, y)
            if best is None or v < bestv:
                best = (x, y)
                bestv = v
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    bestm = None
    bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = abs(tx - nx) + abs(ty - ny)
        bias = 0
        if (nx, ny) == (ox, oy):
            bias = -10
        key = (d + bias, abs(dx) + abs(dy))
        if bestm is None or key < bestd:
            bestm = (dx, dy)
            bestd = key

    if bestm is None:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [int(bestm[0]), int(bestm[1])]