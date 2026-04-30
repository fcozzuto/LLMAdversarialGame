def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []); obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    opp = (ox, oy); selfp = (sx, sy)

    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    def man(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    if not resources:
        targets = [(0, 0), (w-1, h-1), (w-1, 0), (0, h-1)]
        tgt = min(targets, key=lambda p: man(selfp, p))
    else:
        closest_self = min(resources, key=lambda r: cheb(selfp, r))
        closest_opp = min(resources, key=lambda r: cheb(opp, r))
        if tuple(closest_self) == tuple(closest_opp):
            tgt = tuple(closest_self)
        else:
            # contest opponent's nearest resource unless already too close to our own
            ds = cheb(selfp, closest_self); do = cheb(selfp, closest_opp)
            if do <= ds: tgt = tuple(closest_opp)
            else: tgt = tuple(closest_self)
        tgt = (tgt[0], tgt[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic tie-break preference order near target
    pref = sorted(moves, key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]), reverse=False)
    cur_dist = cheb(selfp, tgt)

    best = pref[0]; best_score = -10**9
    res_set = set(tuple(r) for r in resources)

    for dx, dy in pref:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny): continue
        if (nx, ny) in obstacles: continue
        np = (nx, ny)
        dist = cheb(np, tgt)
        score = 0
        score += (cur_dist - dist) * 5  # progress
        if np in res_set: score += 50  # collect immediately
        # keep away from opponent to reduce interception chances
        d_to_opp = cheb(np, opp)
        score += min(20, d_to_opp) * 2
        # if opponent is close, prefer moves that increase their distance
        if cheb(selfp, opp) <= 2:
            score += (d_to_opp - cheb(selfp, opp)) * 4
        # small bias to stay within grid center
        score += -man(np, (w//2, h//2)) * 0.01
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score; best = (dx, dy)

    return [int(best[0]), int(best[1])]