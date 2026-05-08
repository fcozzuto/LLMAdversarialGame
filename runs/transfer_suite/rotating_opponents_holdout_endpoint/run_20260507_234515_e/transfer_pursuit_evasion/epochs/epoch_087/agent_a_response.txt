def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp_step(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    target_step = (clamp_step(ox - sx), clamp_step(oy - sy))

    def open_neighbors(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in blocked:
                cnt += 1
        return cnt

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        dist = cheb(nx, ny, ox, oy)
        opp_dist = cheb(nx, ny, 0 if target_step[0] < 0 else w - 1, 0 if target_step[1] < 0 else h - 1)
        mobility = open_neighbors(nx, ny)
        # pursuer: minimize distance; evader: maximize distance
        # tie-breakers: prefer higher mobility and keep moving in desired general direction
        dir_align = 1 if (dx == target_step[0] and dy == target_step[1]) else 0
        if is_evader:
            score = (-dist, -opp_dist, -mobility, -dir_align)
            if best_score is None or score < best_score:
                best_score = score
                best = [dx, dy]
        else:
            score = (dist, opp_dist, -mobility, -dir_align)
            if best_score is None or score < best_score:
                best_score = score
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]