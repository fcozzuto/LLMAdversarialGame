def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    def dist(a, b, c, d):
        x = a - c
        y = b - d
        return (x if x >= 0 else -x) + (y if y >= 0 else -y)

    target = (ox, oy)
    if unclaimed:
        best = None
        for tx, ty in unclaimed:
            tscore = dist(sx, sy, tx, ty) * 100000 + dist(tx, ty, ox, oy)
            if best is None or tscore < best:
                best = tscore
                target = (tx, ty)

    tx, ty = target
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    bestm = None
    bests = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            score = dist(nx, ny, tx, ty) * 100000 + dist(nx, ny, ox, oy)
            score += (1 if (dx, dy) == (0, 0) else 0)  # prefer moving
            if bests is None or score < bests:
                bests = score
                bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]