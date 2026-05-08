def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in blocked

    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def best_chase_step(px, py, tx, ty):
        best = (0, 0)
        bestd = None
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, tx, ty)
            if bestd is None or d < bestd:
                bestd = d
                best = (dx, dy)
        return best

    def flee_target_score(tx, ty, now_x, now_y):
        # Prefer: larger distance + avoid being cornered behind obstacles by aiming away from opponent.
        d_now = dist2(now_x, now_y, tx, ty)
        d_opp = dist2(now_x, now_y, ox, oy)
        d_to_opp_after = dist2(now_x, now_y, ox, oy)
        return (d_now, d_opp, -d_to_opp_after)

    if role == "pursuer":
        dx, dy = best_chase_step(sx, sy, ox, oy)
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            return [0, 0]
        return [dx, dy]

    # Evader
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    # Choose a corner that is far and not blocked (or at least reachable next step).
    best_corner = None
    best_c = None
    for cx, cy in corners:
        if (cx, cy) in blocked:
            continue
        if best_corner is None or dist2(sx, sy, cx, cy) > best_c:
            best_corner = (cx, cy)
            best_c = dist2(sx, sy, cx, cy)
    if best_corner is None:
        best_corner = max(corners, key=lambda t: dist2(sx, sy, t[0], t[1]))

    # One-step prediction: assume pursuer moves greedily toward our new position.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        pred_dx, pred_dy = best_chase_step(ox, oy, nx, ny)
        nox, noy = ox + pred_dx, oy + pred_dy
        # If noox/noy in bounds/valid required for chase; best_chase_step ensures it.
        score = (dist2(nx, ny, nox, noy), dist2(nx, ny, best_corner[0], best_corner[1]), -dist2(nx, ny, ox, oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]