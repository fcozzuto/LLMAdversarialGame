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

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def min_obs_dist(x, y):
        if not obstacles:
            return 10
        md = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md

    best = (None, -10**18) if is_evader else (None, 10**18)
    # Deterministic tie-break order: fixed move list order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        md = abs(nx - ox) + abs(ny - oy)
        sq = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        od = min_obs_dist(nx, ny)

        if is_evader:
            # Maximize distance from pursuer, keep away from obstacles, slightly prefer larger squared distance.
            score = md * 2.0 + sq * 0.02 + od * 0.15
        else:
            # Minimize distance to opponent, avoid obstacles, slightly prefer tighter alignment (lower sq).
            score = -md * 2.0 - sq * 0.01 + od * 0.10

        if is_evader:
            if score > best[1]:
                best = ([dx, dy], score)
        else:
            if score < best[1]:
                best = ([dx, dy], score)

    if best[0] is None:
        return [0, 0]
    return best[0]