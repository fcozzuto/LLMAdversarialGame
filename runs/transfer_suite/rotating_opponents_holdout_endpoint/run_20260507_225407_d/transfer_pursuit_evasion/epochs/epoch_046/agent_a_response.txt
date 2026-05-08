def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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
        mode = "evade"
    elif "pursuer" in self_role:
        mode = "pursue"
    else:
        scores = observation.get("scores") or {}
        my_s = 0.0
        op_s = 0.0
        if isinstance(scores, dict):
            my_s = scores.get("self", scores.get("me", scores.get("agent", 0.0))) or 0.0
            op_s = scores.get("opponent", scores.get("opp", scores.get("enemy", 0.0))) or 0.0
        mode = "evade" if float(my_s) >= float(op_s) else "pursue"

    best = None
    best_val = None

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            ddx = nx - ox
            ddy = ny - oy
            dist2 = ddx * ddx + ddy * ddy

            wall_dist = min(nx, w - 1 - nx, ny, h - 1 - ny)
            # Small wall_dist -> hugging walls; big wall_dist -> away from walls
            wall_term = -wall_dist if mode == "evade" else wall_dist

            # Encourage move direction: towards opponent if pursuing, away if evading
            dirx = 0 if ox == nx else (1 if ox > nx else -1)
            diry = 0 if oy == ny else (1 if oy > ny else -1)
            towards = (dx == dirx or dx == 0) and (dy == diry or dy == 0)
            dir_term = 0.15 if (mode == "pursue" and towards) else (-0.15 if mode == "evade" and towards else 0.0)

            # Main objective: maximize distance if evading, minimize if pursuing
            val = dist2 if mode == "evade" else -dist2
            val += 0.07 * wall_term + dir_term

            if best is None or val > best_val:
                best = (dx, dy)
                best_val = val

    return [best[0], best[1]]