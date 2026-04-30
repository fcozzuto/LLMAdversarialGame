def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))
    resources = list(dict.fromkeys(resources))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1)]  # deterministic order

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if resources:
            best_r = None
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                if best_r is None or sd < best_r:
                    best_r = sd
            od = man(ox, oy, resources[0][0], resources[0][1]) if resources else 0
            score = -best_r
        else:
            score = -man(nx, ny, ox, oy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move