def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    target_corner = far_corner if i_am_evader else near_corner

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = (0, 0)
    best_score = None
    my_parity = (sx + sy) & 1

    # Evaluate locally to avoid obstacles and bias toward corner when tied.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_opp = dist2(nx, ny, ox, oy)
        d_to_corner = dist2(nx, ny, target_corner[0], target_corner[1])
        # Small deterministic tie-breakers
        parity_pen = 0 if (((nx + ny) & 1) == my_parity) else 3
        corner_bias = (d_to_corner // 8)
        # When evading: maximize distance to opponent, and also increase distance to nearest corner constraint.
        # When pursuing: minimize distance to opponent, and use corner target as tiebreak.
        if i_am_evader:
            score = d_to_opp - 0.15 * corner_bias - parity_pen
        else:
            score = -d_to_opp - 0.05 * corner_bias - parity_pen
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]