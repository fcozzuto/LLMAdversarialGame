def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                rlist.append((x, y))
    if not rlist:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Identify opponent-preferred resource (closest).
    opp_near = None
    opp_best = 10**9
    for rx, ry in rlist:
        d = md(ox, oy, rx, ry)
        if d < opp_best or (d == opp_best and (rx, ry) < (opp_near[0], opp_near[1]) if opp_near else True):
            opp_best = d
            opp_near = (rx, ry)

    # Choose a target resource where we are relatively closer than opponent.
    best_target = None
    best_val = -10**9
    for rx, ry in rlist:
        self_d = md(sx, sy, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        # Encourage taking resources we reach sooner; discourage contesting opponent's closest.
        val = (opp_d - self_d)
        if opp_near == (rx, ry):
            val -= 1.5
        if self_d == 0:
            val += 1000
        key_t = (rx, ry)
        if val > best_val or (val == best_val and key_t < best_target):
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target
    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Move that greedily reduces distance to target, with a small tie-break for moving away from opponent.
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_after = md(nx, ny, tx, ty)
        opp_after = md(nx, ny, ox, oy)
        score = -self_after * 10 + opp_after * 0.01
        if self_after == 0:
            score += 1000
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]