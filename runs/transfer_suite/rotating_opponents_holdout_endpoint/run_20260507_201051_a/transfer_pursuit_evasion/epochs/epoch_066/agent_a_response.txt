def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    is_evader = ("evad" in self_role) or ("evader" in self_role) or ("escape" in self_role) or ("runner" in self_role)
    if ("purs" in self_role) and is_evader:
        is_evader = False
    if ("purs" in opp_role) and ("evad" in self_role or "evader" in self_role):
        is_evader = True

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best_c = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy) * 2 + (c[0] + c[1]) * 0.01)
        tx, ty = best_c

        best = None
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_goal = cheb(nx, ny, tx, ty)
            penalty = 0
            for adjx, adjy in [(nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1)]:
                if not (0 <= adjx < w and 0 <= adjy < h) or (adjx, adjy) in obstacles:
                    penalty += 0.6
            score = d_opp * 1.7 - d_goal * 1.0 - penalty
            if score > best_score:
                best_score = score
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    # pursuer: greedy pursuit with simple "slide along wall" preference
    target_pref = (ox, oy)
    best = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, target_pref[0], target_pref[1])
        # prefer moves that reduce distance; if tie, prefer cutting diagonally; if still tie, prefer minimizing obstacle proximity
        obstacle_prox = 0
        for adjx, adjy in [(nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1)]:
            if not (0 <= adjx < w and 0 <= adjy < h) or (adjx, adjy) in obstacles:
                obstacle_prox += 1
        diag_bonus = 0.2 if dx != 0 and dy != 0 else 0.0
        score = -d * 2.5 + diag_bonus - obstacle_prox * 0.05
        if score > best_score:
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]