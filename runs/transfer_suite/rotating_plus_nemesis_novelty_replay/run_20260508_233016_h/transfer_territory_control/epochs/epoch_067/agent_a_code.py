def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]

    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    cx, cy = w // 2, h // 2
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # pick a direction target deterministically: closest unclaimed, else toward center, else toward away from opponent
    if unclaimed:
        best_t = None
        best_k = 10**18
        for x, y in unclaimed:
            # slight preference for edge pressure to prevent center monopolization
            k = man(x, y, sx, sy) * 2 + man(x, y, ox, oy)
            if x in (0, w - 1) or y in (0, h - 1):
                k -= 3
            if k < best_k:
                best_k = k
                best_t = (x, y)
        tx, ty = best_t
    else:
        tx, ty = (cx, cy)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        immediate = 0
        if (nx, ny) in oppT:
            immediate = 120  # strong flip threat
        elif (nx, ny) in unclaimed:
            immediate = 35   # secure new territory
        elif (nx, ny) in selfT:
            immediate = 6    # low value but safe

        # shaping: move toward target, away from opponent, toward center
        dist_to_target = man(nx, ny, tx, ty)
        dist_from_opp = man(nx, ny, ox, oy)
        dist_to_center = man(nx, ny, cx, cy)
        score = immediate + (-dist_to_target) * 1.5 + dist_from_opp * 0.4 + (-dist_to_center) * 0.05

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]