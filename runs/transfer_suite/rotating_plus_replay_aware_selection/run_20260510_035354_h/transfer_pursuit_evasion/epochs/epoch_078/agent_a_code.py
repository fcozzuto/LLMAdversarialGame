def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d = abs(nx - ox) + abs(ny - oy)
        corner = (0 if nx not in (0, w - 1) else 1) + (0 if ny not in (0, h - 1) else 1)
        # Evader: maximize distance; also prefer corners. Pursuer: minimize distance; prefer staying closer to center-ish.
        score = d + (0.35 * corner if is_evader else -0.1 * corner)
        # Tie-break deterministically: larger score, then smaller distance, then move order via dx,dy.
        key = (-score, d, dx, dy) if is_evader else (score, d, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        # If trapped, try any valid in-bounds non-obstacle move with fixed order; else stay.
        for dx, dy in [(-1, 0), (0, -1), (0, 1), (1, 0), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best