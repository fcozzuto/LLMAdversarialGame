def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    opp_t = observation.get("opponent_territory") or []
    if not unclaimed and not opp_t:
        return [0, 0]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    self_count = observation.get("self_territory_count", 0)
    opp_count = observation.get("opponent_territory_count", 0)
    behind = self_count < opp_count

    targets = []
    if behind:
        targets = (opp_t + unclaimed)[:48]  # attack when behind
    else:
        targets = (unclaimed + opp_t)[:48]  # expand while ahead

    best = (None, -10**9, 0, 0)  # (target, score, selfd, oppd)
    for tx, ty in targets:
        if not inside(tx, ty):
            continue
        selfd = man(sx, sy, tx, ty)
        oppd = man(ox, oy, tx, ty)
        on_opp = (tx, ty) in set(map(tuple, opp_t)) if opp_t else False
        # If on opponent territory, prefer stealing it (flip on entry).
        steal_bonus = 10 if on_opp else 0
        # Territory-edge claim opponent tends to pressure nearby cells; deny by favoring targets closer to us than opponent.
        tempo = (oppd - selfd) if behind else (selfd - oppd)
        # Also prefer closer targets to reduce time spent.
        score = (tempo * 2.2) + steal_bonus - selfd * (0.9 if behind else 0.6)
        if (tx, ty) == (sx, sy):
            score += 5
        if score > best[1]:
            best = ((tx, ty), score, selfd, oppd)

    tx, ty = best[0] if best[0] is not None else (sx, sy)

    # Choose the neighbor that most improves distance to the chosen target, avoiding obstacles.
    best_move = (0, 0)
    best_md = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        md = man(nx, ny, tx, ty)
        # Small bias to avoid stepping into opponent territory unless it is our target region.
        into_opp = (nx, ny) in set(map(tuple, opp_t)) if opp_t else False
        opp_pen = 0
        if into_opp and (tx, ty) not in set(map(tuple, opp_t)):
            opp_pen = 2
        cand = md + opp_pen
        if cand < best_md or (cand == best_md and (dx, dy) < best_move):
            best_md = cand
            best_move = (dx, dy)

    # If all moves are blocked (shouldn't happen), stay.
    return [int(best_move[0]), int(best_move[1])]