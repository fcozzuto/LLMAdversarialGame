def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    sr = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in sr) or ("hunter" in sr) or ("pred" in sr)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obst_pen(x, y):
        p = 0
        for ex, ey in obs:
            dx, dy = x - ex, y - ey
            d2 = dx * dx + dy * dy
            if d2 == 0:
                return 10**9
            if d2 <= 16:  # within 4 steps
                p += (16 - d2)
        return p

    # Choose target corner deterministically for evader
    best_corner = corners[0]
    best_corner_d = -1
    for cx, cy in corners:
        d = dist2(cx, cy, ox, oy)
        if d > best_corner_d:
            best_corner_d = d
            best_corner = (cx, cy)
    tx, ty = best_corner

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            score = -10**18 if is_pursuer else -10**18
        else:
            d_opp = dist2(nx, ny, ox, oy)
            # Small "zigzag" prediction: aim at where opponent is relative to obstacle-free direction (no memory)
            vx = 1 if ox > nx else (-1 if ox < nx else 0)
            vy = 1 if oy > ny else (-1 if oy < ny else 0)
            # Pursuer wants to reduce distance; evader wants to increase it and move toward a corner.
            if is_pursuer:
                score = -d_opp - 0.08 * abs((nx - sx) - 0) - 0.25 * obst_pen(nx, ny)
                # If we can "cut off" by moving in the direction of opponent relative vector, add a bonus.
                score += 0.02 * (dist2(nx + vx, ny + vy, ox, oy) - d_opp)
            else:
                score = d_opp - 0.35 * obst_pen(nx, ny) - 0.02 * dist2(nx, ny, tx, ty)
                # Extra incentive to reach chosen corner sooner
                score += 0.01 * (dist2(sx, sy, tx, ty) - dist2(nx, ny, tx, ty))
        if best_score is None or (score > best_score):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]