def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    sign = 1 if is_evader else -1

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        cx, cy = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        cx, cy = min(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))

    best_pair = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        d = abs(nx - ox) + abs(ny - oy)
        if is_evader:
            corner_bias = (abs(cx - nx) + abs(cy - ny))
        else:
            corner_bias = - (abs(cx - nx) + abs(cy - ny))

        repulse = 0
        if obs:
            for ax, ay in obs:
                md = abs(nx - ax) + abs(ny - ay)
                repulse += 1.0 / (md + 1.0)

        score = sign * (-d) + 0.05 * corner_bias + 0.25 * repulse * (1 if is_evader else -1)
        pair = (score, -d, dx, dy)  # deterministic tie-break
        if best_pair is None or pair > best_pair:
            best_pair = pair

    if best_pair is None:
        return [0, 0]
    return [best_pair[2], best_pair[3]]