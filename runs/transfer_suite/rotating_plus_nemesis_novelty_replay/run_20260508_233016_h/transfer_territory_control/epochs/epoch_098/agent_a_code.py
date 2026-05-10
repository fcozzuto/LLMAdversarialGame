def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_set = set(tuple(p) for p in unclaimed)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Local target bias: closest unclaimed that is either edge-ish or near opponent
    tx, ty = ox, oy
    if unclaimed:
        best = None
        bestv = None
        for x, y in unclaimed:
            edge = 1 if (x == 0 or x == w - 1 or y == 0 or y == h - 1) else 0
            v = man(x, y, ox, oy) * 2 + man(x, y, sx, sy) - edge * 3
            if best is None or v < bestv:
                best = (x, y)
                bestv = v
        tx, ty = best

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        next_is_opp = (nx, ny) in oppT
        next_is_self = (nx, ny) in selfT
        next_is_unclaimed = (nx, ny) in unclaimed_set

        # Prefer capturing opponent / contesting border, otherwise progress toward target and away from opponent when already safe
        score = 0
        if next_is_opp:
            score += 1200  # strong deterministic capture
        if next_is_unclaimed:
            score += 180  # expansion
        if next_is_self:
            score -= 25   # avoid boring re-entry unless it helps positioning

        # Tactical positioning
        d_to_opp = man(nx, ny, ox, oy)
        d_to_self = man(nx, ny, sx, sy)
        d_to_target = man(nx, ny, tx, ty)

        # If not attacking opp, keep moving toward target and keep some distance from opponent if stepping onto our land
        score += (220 - d_to_target * 10)
        if not next_is_opp:
            score += (d_to_opp * (6 if next_is_self else -3))

        # Slight preference to reduce distance to nearest opponent territory cell (encourage border pressure)
        if oppT:
            mind = None
            for px, py in oppT:
                dd = man(nx, ny, px, py)
                if mind is None or dd < mind:
                    mind = dd
            score += max(0, 80 - mind * 10)

        if best_score is None or score > best_score or (score == best_score and [dx, dy] == best_move):
            best_score = score
            best_move = [dx, dy]

    return best_move