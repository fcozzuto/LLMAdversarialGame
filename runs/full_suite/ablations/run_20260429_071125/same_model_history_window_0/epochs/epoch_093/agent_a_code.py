def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    dxs = (-1, 0, 1)
    candidates = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    # Strategic alternation to avoid repeating a weak policy: switch between "race" and "deny"
    # even: minimize (dist_self - dist_opp*0.6) -> race closer advantage
    # odd: minimize (dist_self*1.2 - dist_opp) -> more deny opponent
    even_turn = (observation["turn_index"] % 2 == 0)
    best = None
    for rx, ry in resources:
        if (rx, ry) == (sx, sy) or (rx, ry) == (ox, oy):
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        score = (ds - 0.6*do) if even_turn else (1.2*ds - do)
        if best is None or score < best[0] or (score == best[0] and (rx, ry) < best[1]):
            best = (score, (rx, ry), ds, do)

    # If every resource is on top of someone, just move toward the best remaining-position target anyway
    if best is None:
        if resources:
            rx, ry = min(resources, key=lambda p: (dist((sx, sy), p), p))
            best_pos = (rx, ry)
        else:
            best_pos = (sx, sy)
    else:
        best_pos = best[1]

    rx, ry = best_pos
    # Prefer moves that reduce our distance; if tie, prefer increasing opponent distance; then deterministic tie-break
    curd = dist((sx, sy), (rx, ry))
    best_move = None
    for dx, dy, nx, ny in candidates:
        nd = dist((nx, ny), (rx, ry))
        if nd == 0:
            return [dx, dy]
        oppd = dist((ox, oy), (rx, ry))
        # Additional bias: if opponent is closer to the target, try to move to a neighbor closer to it too
        val = (nd, -oppd, abs((nx - ox)) + abs((ny - oy)), dx, dy)
        if best_move is None or val < best_move[0]:
            best_move = (val, (dx, dy))
    return [best_move[1][0], best_move[1][1]]