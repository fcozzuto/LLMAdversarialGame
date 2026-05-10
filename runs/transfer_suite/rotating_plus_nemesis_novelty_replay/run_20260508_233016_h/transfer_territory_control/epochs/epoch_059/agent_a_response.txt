def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    unclaimed = observation.get("unclaimed_cells") or []
    if not unclaimed:
        unclaimed = []

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose targets biased to (1) near us and (2) near opponent (edge fighting)
    if unclaimed:
        # deterministic selection without randomness
        def tgt_key(c):
            x, y = c
            return (man(x, y, sx, sy) * 2 + man(x, y, ox, oy)) + (0 if (x, y) in oppT else 5)
        unclaimed = sorted([tuple(c) for c in unclaimed], key=tgt_key)[:24]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not unclaimed:
        # fallback: expand away from opponent while progressing to middle area deterministically
        target = (w // 2, h // 2)
        best = None
        best_score = -10**18
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d_to_mid = man(nx, ny, target[0], target[1])
            d_from_opp = man(nx, ny, ox, oy)
            score = d_from_opp * 3 - d_to_mid
            if score > best_score or (score == best_score and (dx, dy) < best):
                best_score, best = score, (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best = None
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer moves that create a "claim advantage" on nearby unclaimed cells
        my_best = 10**9
        opp_best = 10**9
        edge_bonus = 0

        for tx, ty in unclaimed:
            d1 = man(nx, ny, tx, ty)
            if d1 < my_best:
                my_best = d1
            d2 = man(ox, oy, tx, ty)
            if d2 < opp_best:
                opp_best = d2
            # encourage moving toward cells near opponent territory (edge play)
            if man(tx, ty, ox, oy) <= 2:
                edge_bonus = 2

        # If next cell is currently opponent territory, flipping is possible: encourage only if we gain advantage
        flip_bonus = 0
        if (nx, ny) in oppT:
            flip_bonus = 6 + (opp_best - my_best)  # big if we are closer

        # If already ours, still ok but avoid giving opponent access
        own_penalty = -1 if (nx, ny) not in selfT else 0

        # Main score: minimize our distance to promising unclaimed while maximizing opponent being farther
        claim_adv = opp_best - my_best  # positive means we are closer
        score = claim_adv * 8 - my_best * 1 + edge_bonus + flip_bonus + own_penalty

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score, best = score, (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]