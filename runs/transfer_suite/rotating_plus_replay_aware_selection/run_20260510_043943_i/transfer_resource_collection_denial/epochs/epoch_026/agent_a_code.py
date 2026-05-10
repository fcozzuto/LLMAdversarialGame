def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def min_dist(x, y, pts):
        md = 10**9
        for px, py in pts:
            d = man(x, y, px, py)
            if d < md:
                md = d
        return md if md != 10**9 else 10**9

    any_res = len(resources) > 0
    my_to_res = min_dist(sx, sy, resources) if any_res else 10**9
    opp_to_res = min_dist(ox, oy, resources) if any_res else 10**9

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        dres = min_dist(nx, ny, resources) if any_res else 10**9
        dores = min_dist(nx, ny, [(ox, oy)])  # = our distance to opponent

        my_dist_to_opp = man(nx, ny, ox, oy)
        if any_res:
            opp_dist = min_dist(ox, oy, resources)
        else:
            opp_dist = 10**9

        # Priority: beat opponent on resource race; then minimize our resource distance; then don't drift.
        # Deterministic score:
        race_adv = (opp_dist - dres)  # positive if we get closer than they are
        score = 0
        if any_res:
            score += 1000 * race_adv
            score += -3 * dres
        score += -0.2 * my_dist_to_opp

        # Small preference for progress from current position (reduces loops)
        score += -0.05 * (man(sx, sy, nx, ny))

        # Deterministic tie-break: choose lexicographically smallest (dx,dy) among equals
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]