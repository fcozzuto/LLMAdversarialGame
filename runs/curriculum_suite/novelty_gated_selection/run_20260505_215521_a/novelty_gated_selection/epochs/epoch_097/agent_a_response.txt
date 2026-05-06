def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = (w - 2 if ox > sx else 1), (h - 2 if oy > sy else 1)
        best = (0, 0, 10**9, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                d = manh(nx, ny, tx, ty)
                opp = manh(nx, ny, ox, oy)
                cand = (dx, dy, d, opp)
                if cand[2] < best[2] or (cand[2] == best[2] and cand[3] > best[3]):
                    best = cand
        return [best[0], best[1]]

    # Pick a target where we have a relative advantage (or where opponent is "behind").
    best_target = None
    best_adv = -10**18
    for tx, ty in resources:
        ds = manh(sx, sy, tx, ty)
        do = manh(ox, oy, tx, ty)
        # Favor targets closer to us, and penalize ones opponent can reach no later than us.
        adv = (do - ds) * 10 - ds
        # Slightly prefer staying away from being adjacent to opponent.
        if manh(sx, sy, ox, oy) <= 2:
            adv += (manh(tx, ty, ox, oy) - manh(tx, ty, sx, sy))
        if adv > best_adv:
            best_adv = adv
            best_target = (tx, ty)

    tx, ty = best_target

    # Move one step toward target but avoid stepping into a worse "race" state.
    best = (0, 0, -10**18)
    cur_ds = manh(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        nds = manh(nx, ny, tx, ty)
        ndo = manh(ox, oy, tx, ty)  # opponent position fixed this turn
        # If opponent is at least as close to target as we would be, avoid unless it improves a lot.
        race_pen = 0
        if ndo <= nds:
            race_pen = (nds - ndo + 1) * 50
        # Also avoid moves that reduce our safety while not improving distance.
        safety = manh(nx, ny, ox, oy)
        cur_safety = manh(sx, sy, ox, oy)
        improve = cur_ds - nds
        cand_score = improve * 200 + safety * 3 - race_pen
        if cand_score > best[2]:
            best = (dx, dy, cand_score)

    return [int(best[0]), int(best[1])]