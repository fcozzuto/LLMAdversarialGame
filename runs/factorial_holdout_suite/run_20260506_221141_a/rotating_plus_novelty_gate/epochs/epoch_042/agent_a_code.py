def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b, x, y):
        return abs(a - x) + abs(b - y)

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0)

    # New strategic change: evaluate each possible next step by how it affects the best "win margin"
    # against the opponent for all resources, then break ties by preferring closer arrival.
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Compute best achievable margin from the next position
        best_margin = -10**9
        best_approach = 10**9
        best_r = None
        for rx, ry in resources:
            od = dist(ox, oy, rx, ry)
            nd = dist(nx, ny, rx, ry)
            margin = od - nd  # positive means we are closer
            if (margin > best_margin) or (margin == best_margin and nd < best_approach):
                best_margin = margin
                best_approach = nd
                best_r = (rx, ry)

        # If we are not closer to any resource (best_margin <= 0), we minimize opponent advantage and still progress.
        # Tie-break deterministically by favoring moves that reduce total distance to the selected resource.
        if best_margin <= 0:
            # Prefer higher nd-to-opp gap reduction: i.e., maximize (best_approach - opponent_dist_min) negative, but keep deterministic.
            # Use a second metric: minimize nd while also reducing opponent's closeness (od).
            rx, ry = best_r
            od0 = dist(ox, oy, rx, ry)
            val = -best_margin * 2 + (-best_approach) - 0.01 * od0
        else:
            val = best_margin * 3 - best_approach - 0.01 * dist(ox, oy, nx, ny)

        # Deterministic tie-break using turn parity and move ordering effect
        val += 0.000001 * ((dx + 2 * dy + t) % 7)

        if best is None or val > best:
            best = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]