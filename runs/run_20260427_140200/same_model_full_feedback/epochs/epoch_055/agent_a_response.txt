def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def move_score(nx, ny):
        if resources:
            best_adv = -10**18
            for rx, ry in resources:
                sd = dist2(nx, ny, rx, ry)
                od = dist2(ox, oy, rx, ry)
                adv = od - sd  # positive if we are closer than opponent (squared distance)
                if adv > best_adv:
                    best_adv = adv
            # Small tie-breaker: prefer staying farther from opponent when we can't secure advantage
            return best_adv - 0.02 * dist2(nx, ny, ox, oy)
        # No resources: move to reduce distance to opponent-block line by approaching opponent's side
        cx, cy = (w - 1) // 2, (h - 1) // 2
        return -dist2(nx, ny, cx, cy) + 0.01 * dist2(nx, ny, ox, oy)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = move_score(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]