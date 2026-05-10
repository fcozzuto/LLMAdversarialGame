def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                unclaimed.append((x, y))

    if unclaimed:
        best = None
        bs = None
        for c in unclaimed:
            s = dist(c, (ox, oy)) - dist(c, (sx, sy))
            if best is None or s > bs or (s == bs and (c[0], c[1]) < best):
                best, bs = c, s
        tx, ty = best
    else:
        tx, ty = ox, oy

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    bestm = (0, 0)
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = -dist((nx, ny), (tx, ty)) + 0.1 * dist((nx, ny), (ox, oy))
        if bestscore is None or score > bestscore or (score == bestscore and (dx, dy) < bestm):
            bestscore = score
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]