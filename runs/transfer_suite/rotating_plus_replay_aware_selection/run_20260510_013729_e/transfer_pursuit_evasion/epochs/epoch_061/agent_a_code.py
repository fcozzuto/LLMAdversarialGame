def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or (("pursuer" in opponent_role) or ("hunter" in opponent_role) or ("pursue" in opponent_role))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obstacle_adj_pen(nx, ny):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    pen += 2
        return pen

    # Deterministic tie-break: prefer larger index earlier in deltas by fixed order,
    # and prefer moving diagonally when equally good.
    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist_cheb(nx, ny, ox, oy)

        # Evader: maximize separation and head to farthest corner from pursuer.
        if is_evader:
            far_corner = 0
            for cx, cy in corners:
                dc = dist_cheb(cx, cy, ox, oy)
                if dc > far_corner:
                    far_corner = dc
            to_corner = 0
            best_to = -1
            for cx, cy in corners:
                t = -dist_cheb(nx, ny, cx, cy)  # closer to some corner is good for survival? use farthest-corner bias via coefficient below
                if t > best_to:
                    best_to = t
            corner_bias = -best_to  # smaller dist to the chosen farthest corner
            score = (d * 100) + (corner_bias * 1) - obstacle_adj_pen(nx, ny)
            score_key = score
        else:
            # Pursuer: minimize separation; also avoid obstacles that could stall movement.
            score_key = (-d * 100) - obstacle_adj_pen(nx, ny)

        if best_score is None or score_key > best_score:
            best_score = score_key
            best = (dx, dy)
        elif score_key == best_score and best is not None:
            # prefer diagonal, then non-stay, then smallest dx, then smallest dy deterministically
            def diag_rank(dxy):
                ddx, ddy = dxy
                return (0 if ddx != 0 and ddy != 0 else 1, 0 if not (ddx == 0 and ddy == 0) else 1, abs(ddx), abs(ddy))
            if diag_rank((dx, dy)) < diag_rank(best):
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]