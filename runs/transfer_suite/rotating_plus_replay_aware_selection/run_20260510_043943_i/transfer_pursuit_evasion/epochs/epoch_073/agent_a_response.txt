def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in self_role

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Greedy with deterministic tie-break: prefer diagonal alignment, then toward/away, then stay safer (farther from obstacles)
    best_move = [0, 0]
    best_score = None

    # precompute obstacle distance proxy
    obs_list = list(obstacles)
    def obs_min_dist(x, y):
        md = 10**9
        for bx, by in obs_list:
            d = abs(x - bx)
            if d > md: pass
            dy = abs(y - by)
            if dy > d: d = dy
            if d < md: md = d
        return md if md != 10**9 else 99

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        diag_align = 1 if (dx != 0 and dy != 0) else 0
        toward_x = 1 if (dx != 0 and ((ox > sx and dx > 0) or (ox < sx and dx < 0))) else 0
        toward_y = 1 if (dy != 0 and ((oy > sy and dy > 0) or (oy < sy and dy < 0))) else 0
        align = toward_x + toward_y
        safety = obs_min_dist(nx, ny)

        if is_evader:
            # maximize distance; also prefer moves that keep away from obstacles
            score = (dist, diag_align, align, safety)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        else:
            # minimize distance; prefer diagonal chase, and moves aligned toward opponent; then safety
            score = (-dist, diag_align, align, safety)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]