def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    self_is_evader = ("evader" in role) or ("runner" in role)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_in_grid(x, y):
        return 0 <= x < w and 0 <= y < h

    def obstacle_score(x, y):
        if not obstacles:
            return 0
        md = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md

    best_move = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_in_grid(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        man = abs(nx - ox) + abs(ny - oy)
        cheb = max(abs(nx - ox), abs(ny - oy))
        obsd = obstacle_score(nx, ny)

        # Deterministic tie-break: prefer lower dx, then lower dy in a consistent ordering.
        dx_abs = abs(dx) + 0.001 * abs(dy)

        if self_is_evader:
            # Evader: maximize distance; also prefer staying away from obstacles.
            key = (man, obsd, cheb, -dx_abs)
        else:
            # Pursuer: minimize distance; also prefer staying away from obstacles to keep mobility.
            key = (-man, obsd, -cheb, -dx_abs)

        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]