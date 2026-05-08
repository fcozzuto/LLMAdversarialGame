def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Directional bias: head toward nearest unclaimed; if none, toward expanding away from opponent territory.
    if unclaimed:
        tgt = min(unclaimed, key=lambda p: dist2(sx, sy, p[0], p[1]))
    else:
        tgt = None
    if opp_t:
        opp_near = min(opp_t, key=lambda p: dist2(sx, sy, p[0], p[1]))
    else:
        opp_near = None

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in self_t:
            score += 3
        if (nx, ny) in opp_t:
            # flipping allowed on entry; encourage capture but discourage risky tangling near opponent bulk
            score += 20
            if opp_near:
                score += -2 * (dist2(nx, ny, opp_near[0], opp_near[1]))
        if (nx, ny) in unclaimed:
            score += 12
        if tgt:
            score += -2 * dist2(nx, ny, tgt[0], tgt[1])  # closer to nearest frontier
        if opp_near:
            # avoid running deep into opponent territory except when it's immediately beneficial
            score += -1 * (dist2(nx, ny, opp_near[0], opp_near[1]) == 0)  # slight penalty if colliding with border

        # Prefer moves that increase controllable expansion: leaving self_t toward unclaimed
        if (sx, sy) in self_t and (nx, ny) not in self_t:
            score += 2
        # Small deterministic tie-break: prefer staying slightly less than moving diagonally
        score += -0.01 * (abs(dx) + abs(dy) - 0)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]