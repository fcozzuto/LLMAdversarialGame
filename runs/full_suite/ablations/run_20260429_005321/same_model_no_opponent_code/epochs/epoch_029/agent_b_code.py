def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2 and (r[0], r[1]) not in obstacles:
            resources.append((r[0], r[1]))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not moves:
        return [0, 0]

    # If no resources, go to relative center while keeping distance from opponent.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inside(nx, ny):
                continue
            center_dist = abs(nx - cx) + abs(ny - cy)
            opp_dist = cheb(nx, ny, ox, oy)
            key = (opp_dist, -center_dist, dx, dy)
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        return list(best[1]) if best else [0, 0]

    best_move = None
    best_score = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny):
            continue

        # Evaluate best resource we can contest from next position.
        best_contest = None
        best_target = None
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer making ourselves closer than opponent; strongly penalize becoming farther.
            contest = (opp_d - our_d)
            # Extra bias: slightly prefer nearer resources overall once contested.
            score = contest * 100 - our_d * 3
            if best_contest is None or score > best_contest or (score == best_contest and (rx, ry) < best_target):
                best_contest = score
                best_target = (rx, ry)

        # Add a small positional safety term to avoid walking into opponent while moving.
        safety = cheb(nx, ny, ox, oy)
        final_score = best_contest + safety * 2

        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying.
        tie = (final_score, -abs(dx), -abs(dy), -int(dx == 0 and dy == 0), -dx, -dy)
        if best_score is None or tie > best_score:
            best_score = tie
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]