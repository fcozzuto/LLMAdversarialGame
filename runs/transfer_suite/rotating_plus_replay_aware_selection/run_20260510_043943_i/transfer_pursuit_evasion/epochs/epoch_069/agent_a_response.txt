def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or (("evader" in opp_role) and ("pursuer" not in self_role))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not is_evader:
        # Pursuer: minimize Chebyshev distance; avoid obstacles; deterministic tie-break by dir order.
        best = None
        best_d = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            d = max(abs(nx - ox), abs(ny - oy))
            if d < best_d:
                best_d = d
                best = [dx, dy]
        if best is not None:
            return best
        # Fallback: boundary-safe step toward opponent
    else:
        # Evader: maximize distance; also bias away from corners of pursuer.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        far_corner = corners[0]
        best_corner_val = -1
        for cx, cy in corners:
            val = abs(cx - ox) + abs(cy - oy)
            if val > best_corner_val:
                best_corner_val = val
                far_corner = (cx, cy)
        fx, fy = far_corner

        best = None
        best_d = -1
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            d = max(abs(nx - ox), abs(ny - oy))
            # additional bias: move toward farthest corner (relative to pursuer)
            corner_bias = abs(nx - fx) + abs(ny - fy)
            score = d * 1000 + corner_bias
            if d > best_d or (d == best_d and score > best_score):
                best_d = d
                best_score = score
                best = [dx, dy]
        if best is not None:
            return best

    # Final fallback: greedy single-axis step avoiding obstacles if possible
    cand = []
    dx = 0 if ox == sx else (1 if ox > sx else -1)
    dy = 0 if oy == sy else (1 if oy > sy else -1)
    cand.append((dx, dy))
    cand.append((dx, 0))
    cand.append((0, dy))
    cand.append((0, 0))
    for ddx, ddy in cand:
        nx, ny = sx + ddx, sy + ddy
        if in_bounds(nx, ny):
            return [ddx, ddy]
    return [0, 0]