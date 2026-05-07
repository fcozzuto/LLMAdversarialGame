def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))

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
    if not resources:
        return [0, 0]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # choose the best target this move can "win" first
        move_best = None
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # prefer winning (sd < od), then larger denial margin, then quicker capture
            win_margin = od - sd
            # slight preference for positions that are not dead-end around obstacles
            neigh_block = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    if adx == 0 and ady == 0:
                        continue
                    tx, ty = nx + adx, ny + ady
                    if not ok(tx, ty):
                        neigh_block += 1
            score = (win_margin, -sd, -neigh_block)
            if move_best is None or score > move_best:
                move_best = score

        if move_best is None:
            continue
        if best_score is None or move_best > best_score:
            best_score = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]