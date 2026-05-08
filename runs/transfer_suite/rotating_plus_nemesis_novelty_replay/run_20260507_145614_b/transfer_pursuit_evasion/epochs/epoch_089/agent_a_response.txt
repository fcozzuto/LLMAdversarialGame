def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("tag" in role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def min_obst_d2(x, y):
        if not obst:
            return 10**9
        best = 10**9
        for bx, by in obst:
            d = dist2(x, y, bx, by)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            val = -10**18 if not is_pursuer else 10**18
        else:
            d_opp = dist2(nx, ny, ox, oy)
            d_ob = min_obst_d2(nx, ny)
            d_corner = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
            if is_pursuer:
                # chase: minimize distance to opponent, avoid obstacles
                val = -d_opp - 0.03 * d_corner - 0.2 / (1.0 + d_ob)
                better = best_val is None or val > best_val
            else:
                # evade: maximize distance; also drift toward far corner to reduce pursuit angle
                val = d_opp - 0.02 * d_corner + 0.2 / (1.0 + d_ob)
                better = best_val is None or val > best_val
        if best_val is None or better:
            best_val = val
            best_move = [dx, dy]

    return best_move