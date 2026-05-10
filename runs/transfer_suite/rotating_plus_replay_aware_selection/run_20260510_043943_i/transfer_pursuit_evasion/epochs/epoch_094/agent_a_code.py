def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    opp_is_evader = ("evader" in opp_role) or ("runner" in opp_role) or ("escape" in opp_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_opponent_step(cx, cy):
        best = None
        best_val = None
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, sx, sy)
            val = d if opp_is_evader else -d
            if best_val is None or val > best_val:
                best_val = val
                best = (nx, ny)
        return best if best is not None else (cx, cy)

    def best_self_step(cand_moves):
        best_move = [0, 0]
        best_score = None
        for dx, dy in cand_moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            ox2, oy2 = best_opponent_step(ox, oy)
            d_after = cheb(nx, ny, ox2, oy2)
            # depth-2: choose based on who is trying to increase/decrease distance
            score = d_after if self_is_evader else -d_after
            # tie-break: prefer keeping options (more free neighbors)
            free = 0
            for ddx, ddy in dirs:
                tx, ty = nx + ddx, ny + ddy
                if inside(tx, ty):
                    free += 1
            score = (score, free) if not self_is_evader else (score, free)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        return best_move

    candidates = dirs  # deterministic order
    return best_self_step(candidates)