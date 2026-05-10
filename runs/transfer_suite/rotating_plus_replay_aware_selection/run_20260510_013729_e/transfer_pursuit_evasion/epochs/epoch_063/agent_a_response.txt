def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or ("hunter" in role) or ("pursue" in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = (0, 0)

    def obstacle_penalty(nx, ny):
        if not obs:
            return 0
        md = 999
        for ax, ay in obs:
            d = manh(nx, ny, ax, ay)
            if d < md:
                md = d
        return -md  # closer => larger negative

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        dist = cheb(nx, ny, ox, oy)
        op_clear = 0
        if obs:
            op_clear = -min(manh(ox, oy, ax, ay) for ax, ay in obs)  # deterministic small bias
        pen = obstacle_penalty(nx, ny)

        if is_pursuer:
            # minimize distance; break ties to stay away from obstacles
            score = (-dist * 1000) + (pen * 10) + op_clear * 0.1
        else:
            # maximize distance; break ties to stay away from obstacles
            score = (dist * 1000) + (pen * 10) + op_clear * 0.1

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]