def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("hunter" in role) or ("seeker" in role) or ("pursuer" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_from_opp_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    far_from_self_corner = max(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        dist = abs(nx - ox) + abs(ny - oy)
        if dist == 0:
            score = 1e6 if is_pursuer else -1e6
        else:
            if is_pursuer:
                # Chase while also steering toward limiting opponent's escape (toward corner far from opp).
                # Prefer smaller dist, then align to reduce both coordinate differences.
                xdiff0, ydiff0 = abs(sx - ox), abs(sy - oy)
                xdiff1, ydiff1 = abs(nx - ox), abs(ny - oy)
                coord_gain = (xdiff0 - xdiff1) + (ydiff0 - ydiff1)
                target = far_from_opp_corner
                tx, ty = target
                # "Cut" by moving closer to the line toward target (use distance from a mirror point).
                mirror_x, mirror_y = (ox + (tx - ox)) // 1, (oy + (ty - oy)) // 1
                cut = abs(nx - mirror_x) + abs(ny - mirror_y)
                score = (-dist * 10) + coord_gain * 3 + (-cut * 0.2)
            else:
                # Evader: maximize distance, keep moving away in x/y, and head toward farthest corner from pursuer.
                xdiff0, ydiff0 = abs(ox - sx), abs(oy - sy)
                xdiff1, ydiff1 = abs(ox - nx), abs(oy - ny)
                coord_gain = (xdiff1 - xdiff0) + (ydiff1 - ydiff0)
                tx, ty = far_from_self_corner
                goal = abs(nx - tx) + abs(ny - ty)
                score = (dist * 10) + coord_gain * 3 + (goal * 0.1)

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    return [int(best[0]), int(best[1])]