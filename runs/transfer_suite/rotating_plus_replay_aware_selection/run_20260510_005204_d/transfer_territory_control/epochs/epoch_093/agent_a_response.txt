def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    selfT = set((int(p[0]), int(p[1])) for p in observation.get("self_territory") or [])
    oppT = set((int(p[0]), int(p[1])) for p in observation.get("opponent_territory") or [])
    unclaimed = set((int(p[0]), int(p[1])) for p in observation.get("unclaimed_cells") or [])

    def md(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    unlist = list(unclaimed - obstacles)
    if not unlist:
        target = (ox, oy)
    else:
        best = None
        for tx, ty in unlist:
            t = md(sx, sy, tx, ty) * 2 + md(tx, ty, ox, oy)
            if best is None or t < best[0] or (t == best[0] and (tx, ty) < best[1]):
                best = (t, (tx, ty))
        target = best[1]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    bestm = (0, 0)
    bests = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        inopp = (nx, ny) in oppT
        inun = (nx, ny) in unclaimed
        ins = (nx, ny) in selfT
        score = 0
        if inopp:
            score += 3000
        if inun:
            score += 1200
        if ins:
            score += 250
        if (nx, ny) not in selfT and (nx, ny) not in oppT and (nx, ny) not in unclaimed:
            score += 5
        score -= md(nx, ny, target[0], target[1])
        score -= (md(nx, ny, ox, oy) // 2)
        if bests is None or score > bests or (score == bests and (dx, dy) < bestm):
            bests = score
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]