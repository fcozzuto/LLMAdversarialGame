def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("evade" in role) or ("runner" in role)

    if (sx, sy) == (ox, oy):
        return [0, 0]

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = None

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx >= dy else dy

    cur_dist = cheb(sx, sy, ox, oy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = cheb(nx, ny, ox, oy)
        # Deterministic tie-breakers: prefer moving in direction that improves alignment.
        align_now = (ox - sx) * dx + (oy - sy) * dy
        center_bias = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2) * 1e-6

        # Pursuer: minimize distance; Evader: maximize distance. Add small penalty for stepping away from safe paths.
        if is_evader:
            # Encourage increasing distance and moving roughly opposite the pursuer.
            score = (nd - cur_dist) * 10.0 + (-align_now) * 0.05 + center_bias
        else:
            # Encourage reducing distance and moving toward the pursuer.
            score = (-nd + 0.0) * 10.0 + (align_now) * 0.05 + center_bias

        if best_score is None:
            best_score = score
            best_move = (dx, dy)
        else:
            if is_evader:
                if score > best_score + 1e-12:
                    best_score = score
                    best_move = (dx, dy)
            else:
                if score > best_score + 1e-12:
                    best_score = score
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]