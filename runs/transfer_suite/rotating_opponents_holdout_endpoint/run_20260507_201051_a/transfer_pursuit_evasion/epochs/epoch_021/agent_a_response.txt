def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if x is not None and y is not None:
                obs.add((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("chase" in role) or ("pursuer" in role)

    def best_toward(target_x, target_y, avoid_max=False):
        # score: smaller is better for pursuer; larger is better for evader
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = abs(nx - target_x) + abs(ny - target_y)
            s = -d if not avoid_max else d
            # tie-break deterministically toward moving closer on main axes
            tie = (abs(nx - target_x), abs(ny - target_y), dx, dy)
            if best is None or (s > best_score) or (s == best_score and tie < best):
                best = (dx, dy)
                best_score = s
        return best if best is not None else (0, 0)

    if is_pursuer:
        return list(best_toward(ox, oy, avoid_max=False))
    else:
        # evader moves to increase distance
        return list(best_toward(ox, oy, avoid_max=True))