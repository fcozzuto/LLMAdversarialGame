def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in sr) or ("escape" in sr) or ("runner" in sr)
    is_pursuer = ("purs" in sr) and not is_evader

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If roles are ambiguous, infer pursuer/evader from environment_name
    if not is_pursuer and not is_evader:
        env = (observation.get("environment_name") or "").lower()
        if "evasion" in env:
            is_evader = ("evad" in (observation.get("opponent_role") or "").lower())

    if is_evader:
        # Maximize distance from pursuer, but don't step into obstacles/bounds.
        best = None
        best_score = -10**9
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            # Prefer moving toward farthest corner when tied
            corner_bonus = max(cheb(nx, ny, 0, 0), cheb(nx, ny, 0, h - 1), cheb(nx, ny, w - 1, 0), cheb(nx, ny, w - 1, h - 1))
            # Small penalty for being near obstacles (local potential)
            obstacle_pen = 0
            for (bx, by) in obstacles:
                dd = cheb(nx, ny, bx, by)
                if dd == 0:
                    obstacle_pen += 100
                else:
                    obstacle_pen += 1 / (dd + 1)
            score = dist * 100 + corner_bonus - obstacle_pen
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Default pursuer: minimize distance to opponent with gentle obstacle handling.
    best = None
    best_score = 10**9
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        # Prefer moves that reduce distance; break ties by favoring tighter approach.
        # Also bias to occupy cells with fewer immediate escape routes (local obstacle heuristic).
        escape_routes = 0
        for ddx, ddy in cand:
            tx, ty = nx + ddx, ny + ddy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                escape_routes += 1
        score = dist * 1000 + escape_routes
        if score < best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]