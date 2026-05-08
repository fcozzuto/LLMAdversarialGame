def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    if "evader" in self_role:
        want_away = True
    elif "pursuer" in self_role:
        want_away = False
    else:
        scores = observation.get("scores") or {}
        my_s = 0.0
        op_s = 0.0
        if isinstance(scores, dict):
            my_s = scores.get("self", scores.get("me", scores.get("agent", 0.0))) or 0.0
            op_s = scores.get("opponent", scores.get("opp", scores.get("enemy", 0.0))) or 0.0
        want_away = float(my_s) >= float(op_s)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            val = -10**9 if want_away else 10**9
        else:
            d = manh(nx, ny, ox, oy)
            boundary = int(nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1)
            center_bias = - (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.02
            obs_near = 0
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    if ddx == 0 and ddy == 0:
                        continue
                    ax, ay = nx + ddx, ny + ddy
                    if (ax, ay) in obstacles:
                        obs_near += 1
            obs_pen = obs_near * 0.5
            if want_away:
                val = d + boundary * 0.9 + center_bias - obs_pen
            else:
                val = -d + boundary * 0.1 + center_bias - obs_pen
        if best_val is None or (want_away and val > best_val) or ((not want_away) and val < best_val):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]