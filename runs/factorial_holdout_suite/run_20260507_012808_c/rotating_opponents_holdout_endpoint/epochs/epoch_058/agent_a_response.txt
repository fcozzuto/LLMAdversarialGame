def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev for diagonal moves

    def move_ok(dx, dy):
        nx, ny = sx + dx, sy + dy
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cand = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if move_ok(dx, dy)]
    if not cand:
        return [0, 0]

    best_move = cand[0]
    best_val = -10**18
    my_pos_now = (sx, sy)
    opp_pos = (ox, oy)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        my_pos = (nx, ny)
        val = 0

        # Immediate collection preference
        if my_pos in resources:
            val += 1000 - dist(my_pos_now, my_pos)

        # Target resources: prefer ones where we arrive earlier
        local_best = -10**18
        for r in resources:
            d_my = dist(my_pos, r)
            d_opp = dist(opp_pos, r)
            adv = d_opp - d_my  # positive means we are closer/earlier
            score = adv * 30 - d_my * 3
            # Slightly reduce preference for near-tied situations
            if adv <= 0:
                score -= 10
            # Prefer moving toward more "central" resource locations a bit (tie-break)
            score -= (abs(r[0] - (w - 1) / 2) + abs(r[1] - (h - 1) / 2)) * 0.05
            if score > local_best:
                local_best = score
        val += local_best

        # Discourage moving away from all resources (fallback)
        if val < 0:
            nearest = min(dist(my_pos, r) for r in resources)
            val -= nearest

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]