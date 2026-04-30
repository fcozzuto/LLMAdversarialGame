def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        dx = 0
        dy = 0
        if sx < ox: dx = 1
        elif sx > ox: dx = -1
        if sy < oy: dy = 1
        elif sy > oy: dy = -1
        return [dx, dy]

    best = None
    best_score = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; penalize those opponent can reach first.
        score = (ds - do) + (0.2 * ds)  # deterministic tie-break bias
        # Small tie-break toward resources further from opponent to reduce contention.
        score += 0.01 * (-(man(ox, oy, rx, ry)))
        if best_score is None or score < best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Avoid stepping onto opponent if possible.
        opp_pen = 1000 if (nx, ny) == (ox, oy) else 0
        # Move toward target and, secondarily, away from opponent.
        toward = man(nx, ny, tx, ty)
        away = man(nx, ny, ox, oy)
        # If near target, slightly prefer direct alignment.
        candidates.append((opp_pen + toward - 0.03 * away, dx, dy))

    candidates.sort(key=lambda t: t[0])
    return [int(candidates[0][1]), int(candidates[0][2])]