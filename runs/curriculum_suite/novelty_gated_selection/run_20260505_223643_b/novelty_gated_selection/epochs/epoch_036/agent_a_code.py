def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    # Pick a resource that is close to us but "expensive" for the opponent to reach.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        oppd = md(ox, oy, rx, ry)
        # Prefer: minimize (myd + 2*oppd), then minimize myd, then maximize oppd.
        key = (myd + 2 * oppd, myd, -oppd)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Step greedily toward the chosen target, with denial tie-break: keep opponent farther from that target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my_after = md(nx, ny, tx, ty)
        opp_dist = md(ox, oy, tx, ty)
        # Opp dist doesn't change this turn, but keep tie-break consistent if targets ever swap.
        score = (my_after, -opp_dist, abs(nx - tx) + abs(ny - ty))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]