def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # deterministic heuristic:
    # prioritize moving toward nearest resource, then away from opponent to prevent block.
    best = None
    best_score = -10**9
    for dx, dy, nx, ny in cand:
        score = 0
        if resources:
            # Chebyshev distance to closest resource
            dR = min(max(abs(nx - rx), abs(ny - ry)) for rx, ry in resources)
            score -= dR * 2
        # prefer staying closer to center if ambiguous
        center_x, center_y = w // 2, h // 2
        dist_center = max(abs(nx - center_x), abs(ny - center_y))
        score -= dist_center * 0.1
        # avoid colliding with opponent: if moving adjacent to opponent, prefer smaller proximity difference
        dist_opp = max(abs(nx - ox), abs(ny - oy))
        if dist_opp == 0:
            score -= 5
        else:
            score += 0 if dist_opp > 1 else -1
        if score > best_score or best is None:
            best_score = score
            best = (dx, dy, nx, ny)

    if best is None:
        return [0, 0]
    dx, dy, nx, ny = best
    return [dx, dy]