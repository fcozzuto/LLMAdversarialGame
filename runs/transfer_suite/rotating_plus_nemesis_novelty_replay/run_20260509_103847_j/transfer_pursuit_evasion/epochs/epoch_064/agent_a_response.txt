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

    role = (observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "escape", "evade", "runner"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_score = None

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Target for evader: farthest corner from pursuer; for pursuer: nearest corner to own opposite side is not needed, but tie-break helps.
    if is_evader:
        tc = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))
    else:
        tc = min(corners, key=lambda c: manh(c[0], c[1], ox, oy))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if nx == ox and ny == oy:
            continue  # don't step onto opponent when avoidable
        d = manh(nx, ny, ox, oy)
        # Primary objective: evader maximize distance, pursuer minimize distance.
        # Secondary objective: move towards chosen corner (evader maximize, pursuer minimize) for deterministic structure.
        corner_d = manh(nx, ny, tc[0], tc[1])
        # Tertiary objective: prefer higher local mobility to avoid dead-ends.
        mobility = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if valid(ax, ay):
                mobility += 1

        if is_evader:
            score = (d, corner_d, mobility)  # maximize d, then maximize corner_d (move away from corner target)
            # But corner_d is distance to tc; we want to increase distance to pursuer-oriented farthest corner, which is small-to-tc for being there.
            # For farthest-corner tc, staying away increases corner_d, so OK.
            maximize = True
        else:
            score = (-d, -corner_d, mobility)  # minimize d, minimize corner_d, then maximize mobility
            maximize = True

        if best_score is None:
            best_score = score
            best = [dx, dy]
        else:
            if maximize:
                if score > best_score:
                    best_score = score
                    best = [dx, dy]
            else:
                if score < best_score:
                    best_score = score
                    best = [dx, dy]

    if best is None:
        # fallback: deterministic stay
        return [0, 0]
    return best