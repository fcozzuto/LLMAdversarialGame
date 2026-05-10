def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "fugitive"))
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "seeker"))
    if not is_evader and not is_pursuer:
        is_pursuer = True

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort(key=lambda m: (m[0], m[1]))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    best = None
    best_val = -10**9 if is_evader else 10**9
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obs:
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val = dist2 if is_evader else -dist2
        if is_evader:
            if val > best_val:
                best_val, best = val, [dx, dy]
        else:
            if val < best_val:
                best_val, best = val, [dx, dy]

    if best is not None:
        return best

    for dx, dy in moves:
        return [dx, dy]
    return [0, 0]