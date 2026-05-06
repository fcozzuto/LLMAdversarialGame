def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w, h = observation.get("grid_width", 0), observation.get("grid_height", 0)
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        ax, ay, bx, by = int(ax), int(ay), int(bx), int(by)
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    best_move = legal[0]
    best_score = None

    # Target: nearest resource (tie-breaker: lowest (x,y))
    target = None
    if resources:
        best_t = None
        best_d = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                d = man(sx, sy, rx, ry)
                if best_d is None or d < best_d or (d == best_d and (rx, ry) < best_t):
                    best_d, best_t = d, (rx, ry)
        target = best_t

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if target is not None:
            # Prefer closer to our target; slightly avoid being closer to opponent than us
            score = man(nx, ny, target[0], target[1])
            opp_adv = man(nx, ny, ox, oy) - man(ox, oy, sx, sy)
            score += 0.1 * opp_adv
        else:
            # No resources: move to reduce distance to opponent
            score = man(nx, ny, ox, oy) - 0.1 * man(nx, ny, sx, sy)

        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]