def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    tx, ty = sx, sy
    if unclaimed:
        best = None
        best_val = None
        for x, y in unclaimed:
            edge = min(x, y, w - 1 - x, h - 1 - y)
            val = edge * 50 - dist(x, y, ox, oy) * 3 - dist(x, y, sx, sy)
            if best_val is None or val > best_val or (val == best_val and (x, y) < best):
                best_val = val
                best = (x, y)
        tx, ty = best

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        toward = dist(nx, ny, tx, ty)
        away_opp = dist(nx, ny, ox, oy)
        score = -toward * 10 + away_opp * 2 + (1 if (nx, ny) == (tx, ty) else 0)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if inb(sx + best_move[0], sy + best_move[1]):
        return [int(best_move[0]), int(best_move[1])]
    for dx, dy in dirs:
        if inb(sx + dx, sy + dy):
            return [int(dx), int(dy)]
    return [0, 0]