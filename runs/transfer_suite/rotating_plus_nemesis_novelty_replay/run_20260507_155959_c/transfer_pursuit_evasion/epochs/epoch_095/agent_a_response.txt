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
    pursue = (not self_evader) or opp_evader

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    # Deterministic tie-break order: keep earlier moves if equal.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy

        # Prefer moves that keep options around the landing square (avoid tight corners).
        free_nb = 0
        for mx, my in moves:
            tx, ty = nx + mx, ny + my
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obs:
                free_nb += 1

        # Minor "direction" nudge to avoid oscillations: align with current vector to opponent.
        dir_align = (1 if dx * (ox - sx) > 0 else -1 if dx * (ox - sx) < 0 else 0) + \
                     (1 if dy * (oy - sy) > 0 else -1 if dy * (oy - sy) < 0 else 0)

        if pursue:
            score = (-dist2) + 0.08 * free_nb + 0.01 * dir_align
        else:
            score = (dist2) + 0.08 * free_nb + 0.01 * dir_align

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]