def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "evasion"))
    is_chaser = any(k in role for k in ("pursuer", "chaser", "catcher"))
    if not is_evader and not is_chaser:
        is_evader = False
        is_chaser = False

    want_away = is_evader and not is_chaser

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = None
    best_corner_d = -1
    for cx, cy in corners:
        d2 = (cx - ox) * (cx - ox) + (cy - oy) * (cy - oy)
        if d2 > best_corner_d:
            best_corner_d = d2
            best_corner = (cx, cy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        if want_away:
            # Maximize distance; also steer toward farthest corner from opponent (break ties).
            tx, ty = best_corner
            corner_d2 = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            edge = (nx in (0, w - 1)) + (ny in (0, h - 1))
            score = (dist2 * 1000) + (-corner_d2) + (edge * 3)
        else:
            # Pursue: minimize distance; prefer moves that align with opponent direction.
            dir_align = 0
            dir_align += 1 if (ox - nx) * (ox - sx) > 0 else 0
            dir_align += 1 if (oy - ny) * (oy - sy) > 0 else 0
            center = (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            score = (-dist2 * 1000) + (dir_align * 10) - (center)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]