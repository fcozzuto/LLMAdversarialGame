def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cx, cy = w // 2, h // 2

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            sd = dist2(sx, sy, rx, ry)
            od = dist2(ox, oy, rx, ry)
            # maximize "we are closer than opponent" (od - sd). Tie-break deterministically.
            key = (-(od - sd), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)

        tx, ty = best_r
        best_move = [0, 0]
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            self_d = dist2(nx, ny, tx, ty)
            opp_d = dist2(ox, oy, tx, ty)
            center_pen = dist2(nx, ny, cx, cy) * 0.001
            # Encourage getting closer than opponent (in terms of squared distance).
            score = (self_d - opp_d) + center_pen
            # Also slightly discourage moving directly toward opponent if it doesn't reduce target distance.
            opp_pen = dist2(nx, ny, ox, oy) * 0.0005
            score += -opp_pen if self_d >= dist2(sx, sy, tx, ty) else 0.0
            move_key = (score, abs(dx) + abs(dy), nx, ny)
            if best_score is None or move_key < best_score:
                best_score = move_key
                best_move = [dx, dy]
        return best_move

    # No resources: drift toward center while keeping away from opponent a bit.
    cur_d_center = dist2(sx, sy, cx, cy)
    cur_d_opp = dist2(sx, sy, ox, oy)
    best = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dC = dist2(nx, ny, cx, cy)
        dO = dist2(nx, ny, ox, oy)
        key = (dC, -(dO), abs(dx) + abs(dy), nx, ny, 0 if cur_d_center == dC else 1)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    return best