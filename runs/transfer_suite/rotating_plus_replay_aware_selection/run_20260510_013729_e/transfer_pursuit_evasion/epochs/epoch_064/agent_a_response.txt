def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.append((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or ("hunter" in role) or ("pursue" in role)

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Obstacle avoidance: penalize closeness.
        pen = 0
        for ax, ay in obs:
            d = manh(nx, ny, ax, ay)
            if d == 0:
                pen += 10000
            else:
                pen += 24 // d  # larger when closer

        # Pursuer: minimize distance to opponent; Evader: maximize it.
        d_to_op = manh(nx, ny, ox, oy)

        if is_pursuer:
            val = -d_to_op - pen
        else:
            # Also prefer moving toward safer corners depending on opponent.
            corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
            best_corner_dist = 0
            for cx, cy in corners:
                best_corner_dist = max(best_corner_dist, manh(cx, cy, ox, oy))
            # Encourage moving away from opponent and toward farthest-corner direction.
            # Compute "corneriness" by distance to farthest corner from opponent.
            far_corner = None
            far_cd = -1
            for cx, cy in corners:
                cd = manh(cx, cy, ox, oy)
                if cd > far_cd:
                    far_cd = cd
                    far_corner = (cx, cy)
            cx, cy = far_corner
            to_far_corner = manh(nx, ny, cx, cy)
            val = d_to_op * 2 - pen * 1.5 - to_far_corner * 0.2 + best_corner_dist * 0.01

        if best is None or val > best:
            best = val
            best_move = [dx, dy]

    return best_move