def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "flee"))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def blocked(x, y):
        return (x, y) in obstacles or x < 0 or x >= w or y < 0 or y >= h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Aim: pursuer reduce distance; evader increase distance.
    # Tie-break: prefer safer squares (fewer blocked neighbors), and steer toward/away from corners.
    def score_cell(nx, ny):
        md = abs(nx - ox) + abs(ny - oy)
        corner_bias = 0
        # distance to nearest corner (larger = farther from corner)
        dcorner = min(nx + ny, nx + (h - 1 - ny), (w - 1 - nx) + ny, (w - 1 - nx) + (h - 1 - ny))
        # If evader: prefer smaller dcorner when opponent is near (escape tends to corner).
        if is_evader:
            md_score = -md
            corner_bias = -dcorner
        else:
            md_score = md * -1  # maximize negative distance => minimize md
            corner_bias = dcorner * 0  # keep neutral
        # safety: count blocked adjacent (including self staying allowed)
        b = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if blocked(nx + dx, ny + dy):
                    b += 1
        safety = -b if not is_evader else -b  # both prefer less blocked
        # slight preference to progress in intended direction via dx/dy relative sign to target
        prog = 0
        if not is_evader:
            prog = - (abs((nx - sx)) + abs((ny - sy))) * 0.01
        else:
            prog = - (abs((nx - sx)) + abs((ny - sy))) * 0.01
        return md_score + safety * 1.5 + corner_bias * 0.05 + prog

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        val = score_cell(nx, ny)
        key = (val, -dx, -dy)  # deterministic tie-break
        if best is None or key > best:
            best = key
            best_val = (dx, dy)

    # If fully blocked (rare), stay.
    if best_val is None:
        return [0, 0]
    return [int(best_val[0]), int(best_val[1])]