def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    if not resources:
        tx, ty = (W // 2, H // 2)
        best = (0, 0)
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = -cd(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_key = None

    cx, cy = W - 1 - ox, H - 1 - oy  # deterministic "mirror" pressure point

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_target_score = None
        for rx, ry in resources:
            ds = cd(nx, ny, rx, ry)
            do = cd(ox, oy, rx, ry)
            if ds == 0:
                score = 10**6
            else:
                score = (do - ds) * 100 - ds * 2 + (rx * 0.01 + ry * 0.001)
            if best_target_score is None or score > best_target_score:
                best_target_score = score

        # Secondary tie-breakers: reduce own distance to "contested center line" and avoid opponent chase
        opp_dist_now = cd(nx, ny, ox, oy)
        center_dist = cd(nx, ny, cx, cy)
        key = (best_target_score, opp_dist_now, -center_dist, -cd(nx, ny, W - 1 - nx, H - 1 - ny))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]