def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        ax = a - c; ax = -ax if ax < 0 else ax
        ay = b - d; ay = -ay if ay < 0 else ay
        return ax if ax > ay else ay

    res = [tuple(r) for r in resources]
    res_set = set(res)

    # If we can collect immediately, do it.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    # If opponent is about to collect a resource, contest it.
    contest = None
    for rx, ry in res:
        if cheb(ox, oy, rx, ry) == 1:
            contest = (rx, ry)
            break

    # Evaluate candidate moves with a deterministic scoring heuristic.
    best = None; best_score = -10**18
    cand = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not cand:
        return [0, 0]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        score = 0
        if contest is not None:
            rx, ry = contest
            # Push directly toward contest target; if equal, still prefer closer.
            score += 1000 - cheb(nx, ny, rx, ry)
            score += 50 * (cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry))
        if res:
            # Find best "advantage" resource for us after this move.
            best_adv = -10**9
            best_selfd = 10**9
            for rx, ry in res:
                selfd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                adv = oppd - selfd
                if adv > best_adv or (adv == best_adv and selfd < best_selfd):
                    best_adv = adv; best_selfd = selfd
            # Prefer resources where we are (or become) earlier than opponent; otherwise closest.
            score += 10 * best_adv - best_selfd
        # Tie-break deterministically: prefer larger score, then fewer remaining steps to opponent (slight interference).
        score += -0.01 * cheb(nx, ny, ox, oy)

        if score > best_score:
            best_score = score; best = [dx, dy]

    return best if best is not None else [0, 0]