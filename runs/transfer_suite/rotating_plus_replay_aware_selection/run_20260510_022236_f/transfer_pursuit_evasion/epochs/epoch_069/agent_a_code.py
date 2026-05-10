def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("flee" in role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = min(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_target = abs(nx - tx) + abs(ny - ty)

        if is_evader:
            # Prefer moving away from pursuer; also bias toward a far corner.
            val = (-d_opp, d_target, abs(dx) + abs(dy))
        else:
            # Prefer reducing distance to opponent; if blocked, drift toward best corner.
            val = (d_opp, d_target, abs(dx) + abs(dy))

        if best is None or (val < best_val):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]