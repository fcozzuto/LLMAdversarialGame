def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist8(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Prefer resources where we are closer than opponent, and avoid letting opponent easily take "their side" row.
    best = None
    for r in resources:
        dm = dist8((sx, sy), r)
        do = dist8((ox, oy), r)
        # Edge-patrol bias: oppose their likely path along y; slightly punish being on same y band.
        row_pen = 2 if r[1] == oy else 0
        # Strongly prefer advantage, then closer.
        val = ((do - dm) - row_pen, -(dm), -abs(r[0] - (w - 1 if oy < h // 2 else 0)), r[0], r[1])
        if best is None or val > best[0]:
            best = (val, r)
    target = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate move by progress to target and reducing opponent's advantage on that target.
        dme = dist8((nx, ny), target)
        dse = dist8((ox, oy), target)
        score = (dse - dme, -dme, -abs((nx - sx)) - abs((ny - sy)), -abs(nx - target[0]), -abs(ny - target[1]))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]