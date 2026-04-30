def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) if abs(x1 - x2) > abs(y1 - y2) else abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Select a deterministic target: prioritize contested, then favor (opponent lead we can overturn), then safety/center.
    best = None
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        contest = 1 if myd <= opd else 0
        # obstacle adjacency penalty for landing at target neighborhood
        adj = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (tx + dx, ty + dy) in obstacles:
                    adj += 1
        center = -(abs(tx - (w - 1) / 2) + abs(ty - (h - 1) / 2))
        key = (contest, opd - myd, -myd, -adj, center, tx, ty)
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = (0, 0)

    # Greedy one-step: move that most reduces distance to target while considering safety and denying opponent approach.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd2 = md(nx, ny, tx, ty)
        opd2 = md(ox, oy, tx, ty)  # opponent unchanged this step
        # Adjacency penalty for safety around next cell
        adj2 = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj2 += 1
        # Deny: if we can reduce our lead gap vs opponent at the target by moving closer
        lead_progress = (opd2 - myd2) - (opd2 - md(sx, sy, tx, ty))
        # Deterministic tie-break uses turn_index parity
        parity = observation.get("turn_index", 0) & 1
        score = (-myd2, -adj2, -abs(nx - tx) - abs(ny - ty), -(myd2 <= opd2), lead_progress, (dx + dy) * (1 if parity == 0 else -1), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]