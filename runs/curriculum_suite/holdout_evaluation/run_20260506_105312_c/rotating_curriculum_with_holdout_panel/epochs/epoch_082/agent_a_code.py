def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                rlist.append((x, y))
    if not rlist:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    def md(ax, ay, bx, by):
        d = abs(ax - bx) + abs(ay - by)
        return d

    # Target resources the opponent is closer to (we can contest), else nearest overall.
    best_targets = []
    for rx, ry in rlist:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        diff = do - ds  # positive means we are closer already
        best_targets.append((diff, ds, do, rx, ry))
    best_targets.sort(key=lambda t: (t[0], -t[2]))  # maximize (do-ds), tie favor smaller do (more contest)

    # Consider top few contested/near options deterministically
    candidate_resources = []
    for t in best_targets:
        candidate_resources.append((t[3], t[4]))
        if len(candidate_resources) >= 3:
            break

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # immediate advantage: for contested targets, maximize (opp_dist - self_dist) after move
        score = 0
        for rx, ry in candidate_resources:
            ds2 = md(nx, ny, rx, ry)
            do2 = md(ox, oy, rx, ry)
            score += (do2 - ds2)

        # secondary: move toward the single closest target to reduce absolute distance
        closest = min(md(nx, ny, rx, ry) for rx, ry in candidate_resources)
        score = (score, -closest)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # tie-break: deterministic prefer smaller dx, then smaller dy
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]