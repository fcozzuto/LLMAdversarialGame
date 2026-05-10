def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d_op = abs(nx - ox) + abs(ny - oy)
        score = -d_op if is_pursuer else d_op

        # tie-break: prefer not to stay if possible, and prefer moving toward center if roles ambiguous
        if dx == 0 and dy == 0:
            score -= 1
        cx, cy = (w - 1) // 2, (h - 1) // 2
        score += -(abs(nx - cx) + abs(ny - cy)) * (0.001 if not is_pursuer else -0.001)

        if best is None or score > best_val:
            best = [dx, dy]
            best_val = score

    if best is None:
        return [0, 0]
    return best