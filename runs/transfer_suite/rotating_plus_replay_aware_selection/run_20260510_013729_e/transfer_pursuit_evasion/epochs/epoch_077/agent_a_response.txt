def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_ev = ("evad" in self_role) or ("run" in self_role) or ("escap" in self_role)
    opp_ev = ("evad" in opp_role) or ("run" in opp_role) or ("escap" in opp_role)
    pursuer = (not self_ev) or opp_ev  # if opponent is evading, we pursue

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    goal = min(corners, key=lambda t: md(t[0], t[1], ox, oy)) if not pursuer else max(corners, key=lambda t: md(t[0], t[1], ox, oy))

    best = None
    best_score = None
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_to_opp = md(nx, ny, ox, oy)
        d_to_goal = md(nx, ny, goal[0], goal[1])

        # obstacle proximity penalty (deterministic, mild)
        prox = 0
        for ax, ay in obstacles:
            dd = md(nx, ny, ax, ay)
            if dd == 0:
                prox -= 50
            elif dd == 1:
                prox -= 3
            elif dd == 2:
                prox -= 1

        if pursuer:
            score = (-d_to_opp * 10) + (0.5 * d_to_goal) + prox
        else:
            score = (d_to_opp * 10) + (-0.3 * d_to_goal) + prox

        # deterministic tie-break
        key = (score, -dx, -dy) if best_score is None or score != best_score else (score, -dx, -dy)
        if best_score is None or score > best_score or (score == best_score and (-dx, -dy) > (-best[0], -best[1])):
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]