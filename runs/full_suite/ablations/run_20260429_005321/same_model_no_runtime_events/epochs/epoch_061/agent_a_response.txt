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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not valid(sx, sy):
        for dx, dy in dirs:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    cx, cy = w // 2, h // 2
    best_move = [0, 0]
    best_score = -10**18

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Move toward center while keeping distance from opponent
            score = -cheb(nx, ny, cx, cy) + 0.8 * cheb(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Pick a contested resource: close to us, far from opponent
        local_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = -ds + 1.3 * do - 0.08 * (abs(nx - rx) + abs(ny - ry))
            if val > local_best:
                local_best = val
        # Mild bias to not let opponent approach us too directly
        opp_pressure = 0.18 * cheb(nx, ny, ox, oy)
        score = local_best - opp_pressure
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move