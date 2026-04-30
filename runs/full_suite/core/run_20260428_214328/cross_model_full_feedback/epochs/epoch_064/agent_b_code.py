def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    def dist_cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    target = None
    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            d = dist_cheb((sx, sy), (rx, ry))
            od = dist_cheb((ox, oy), (rx, ry))
            score = (d, od)
            if best_score is None or score < best_score:
                best = (rx, ry)
                best_score = score
        target = best

    if target is not None:
        dx = target[0] - sx
        dy = target[1] - sy
        move = [0, 0]
        if dx != 0: move[0] = 1 if dx > 0 else -1
        if dy != 0: move[1] = 1 if dy > 0 else -1
        nx, ny = sx + move[0], sy + move[1]
        if (move[0] == 0 and move[1] == 0) or not inside(nx, ny) or (nx, ny) in obstacles:
            return [0, 0]
        return move

    # Fallback: move toward center or away from obstacle/opponent deterministically
    target_cx, target_cy = w // 2, h // 2
    dx = target_cx - sx
    dy = target_cy - sy
    move = [0, 0]
    if dx != 0: move[0] = 1 if dx > 0 else -1
    if dy != 0: move[1] = 1 if dy > 0 else -1
    nx, ny = sx + move[0], sy + move[1]
    if (move[0] == 0 and move[1] == 0) or not inside(nx, ny) or (nx, ny) in obstacles:
        # try small detour
        alt = [[-1,0],[1,0],[0,-1],[0,1],[-1,-1],[1,1],[-1,1],[1,-1]]
        for ax, ay in alt:
            tx, ty = sx + ax, sy + ay
            if inside(tx, ty) and (tx, ty) not in obstacles:
                return [ax, ay]
        return [0,0]
    return move