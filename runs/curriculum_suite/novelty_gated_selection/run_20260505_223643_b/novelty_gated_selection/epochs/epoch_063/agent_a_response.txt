def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (-1, -1), (1, -1), (0, 1), (-1, 1), (1, 1)]

    def md2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Deterministic tie-breaking: prefer smaller dx/dy lexicographically.
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Avoid getting trapped near opponent: if opponent can land on us next, penalize.
        opp_next_close = md2(nx, ny, ox, oy) <= 1
        score = 0
        best_resource_gap = -10**18

        for rx, ry in resources:
            d_self = md2(nx, ny, rx, ry)
            d_opp = md2(ox, oy, rx, ry)
            # Prefer resources where we have an advantage over the opponent.
            gap = (d_opp - d_self)  # larger is better
            if gap > best_resource_gap:
                best_resource_gap = gap
            # Small bonus for moving toward any resource to keep progress.
            score += 0.02 * (1.0 / (1.0 + d_self))

        # Main objective: maximize advantage gap to some resource.
        # Penalize if we are too close to opponent (helps against sweeping/pursuit).
        score += best_resource_gap * 1.2
        if opp_next_close:
            score -= 4.0

        # Secondary objective: keep distance from obstacles "softly" by preferring cells farther from obstacle list center.
        if obstacles:
            oxm = sum(o[0] for o in obstacles) / len(obstacles)
            oym = sum(o[1] for o in obstacles) / len(obstacles)
            score += 0.01 * md2(nx, ny, int(oxm), int(oym))

        if best is None or score > best or (score == best and (dx, dy) < (best_move[0], best_move[1])):
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]