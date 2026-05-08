def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or (self_role == "evader")
    opp_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or (opp_role == "evader")

    # If we are pursuer, chase. If we are evader, flee.
    chase = (not self_evader) or opp_evader

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def obstacle_penalty(x, y):
        # Strongly avoid stepping onto/adjacent to obstacles.
        if (x, y) in obs:
            return 10_000
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    pen += 120 if (ax == 0 or ay == 0) else 90
        return pen

    def score_cell(x, y):
        dx, dy = x - ox, y - oy
        d2 = dx * dx + dy * dy
        # Prefer staying off obstacles and prefer goal behavior (chase vs flee).
        base = d2 if chase else -d2
        return base + obstacle_penalty(x, y) + (0.2 * (abs(dx) + abs(dy)))

    best = None
    best_sc = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        sc = score_cell(nx, ny)
        if best_sc is None or (sc < best_sc if chase else sc > best_sc):
            best_sc = sc
            best = (mx, my)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]