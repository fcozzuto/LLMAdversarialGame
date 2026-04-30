def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    targets = resources if resources else []
    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        return abs(dx) + abs(dy)

    if targets:
        best = None
        for r in targets:
            d = dist((sx, sy), r)
            key = (d, r[0], r[1])
            if best is None or key < best[0]:
                best = (key, r)
        tx, ty = best[1]
    else:
        # No resources visible: move toward center to stabilize.
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    opp = (ox, oy)
    candidates = []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic order for ties: prefer smaller (dx,dy) lexicographically after best score.
    moves.sort(key=lambda m: (m[0], m[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if targets:
            dt = dist((nx, ny), (tx, ty))
        else:
            dt = abs(nx - tx) + abs(ny - ty)
        do = dist((nx, ny), opp)
        # Primary: get closer to target; Secondary: stay away from opponent; slight preference for collecting soon.
        score = (-dt) + 0.05 * do
        if targets:
            # If resource is adjacent, strongly prefer it.
            score += -0.3 * min(dist((nx, ny), r) for r in targets)
        # Tie-break key: higher score better; then closer to target; then deterministic position.
        key = (-score, dt, nx, ny, dx, dy)
        candidates.append((key, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]