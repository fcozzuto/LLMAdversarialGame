def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    self_role = str(observation.get("self_role") or "")
    opp_role = str(observation.get("opponent_role") or "")
    self_evader = "evader" in self_role.lower()
    opponent_evader = "evader" in opp_role.lower()

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    fc_x, fc_y = far_corner

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d2 = dist2(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)
        to_corner = dist2(nx, ny, fc_x, fc_y)

        # Role-based objective with obstacle-safe tie breaks.
        if self_evader:
            # Run to maximize separation, but also drift toward the farthest corner for longer-term advantage.
            val = (d2, to_corner, -man)
            want_max = True
        else:
            # Pursue by minimizing distance; add corner-gravity to reduce escape potential in pursuit-direct.
            # If opponent is an evader, corner-gravity helps cut off.
            if opponent_evader:
                val = (-d2, -to_corner, man)
            else:
                val = (-d2, -(abs(nx - fc_x) + abs(ny - fc_y)), man)
            want_max = True  # we constructed negated metrics for max

        if best_val is None:
            best_val = val
            best_move = [dx, dy]
        else:
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]