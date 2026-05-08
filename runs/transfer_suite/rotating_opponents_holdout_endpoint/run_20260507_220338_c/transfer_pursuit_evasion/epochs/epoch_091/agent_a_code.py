def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_evader = not any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def cheb(x, y, tx, ty):
        dx = abs(x - tx)
        dy = abs(y - ty)
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    best_move = [0, 0]
    best_score = None

    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_to_opp = cheb(nx, ny, ox, oy)

            # deterministic tie-break: fixed ordering weight from dx,dy
            tie = (dx + 1) * 9 + (dy + 1)

            if i_am_evader:
                # Flee from pursuer, and bias toward the corner farthest from opponent
                # Also discourage moving "toward" the opponent in Chebyshev terms.
                corner_bias = cheb(nx, ny, best_corner[0], best_corner[1])
                score = (d_to_opp * 1000) + (corner_bias * 2) + ((dx != 0 or dy != 0) * 0.1) + (tie * 1e-6)
            else:
                # Pursue: minimize Chebyshev distance; prefer moves that also increase cornering pressure
                corner_opp = cheb(nx, ny, best_corner[0], best_corner[1])
                score = (-d_to_opp * 1000) + (corner_opp * 0.5) + ((dx != 0 or dy != 0) * 0.1) + (tie * 1e-6)

            if best_score is None:
                best_score = score
                best_move = [dx, dy]
            else:
                if i_am_evader:
                    if score > best_score:
                        best_score = score
                        best_move = [dx, dy]
                else:
                    if score > best_score:
                        best_score = score
                        best_move = [dx, dy]

    return best_move