def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            res.append((px, py))
            resset.add((px, py))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    if res:
        for dx0, dy0 in deltas:
            nx, ny = x + dx0, y + dy0
            if not inb(nx, ny):
                continue
            if (nx, ny) in resset:
                return [dx0, dy0]

            best_t = -10**18
            for rx, ry in res:
                myd = md(nx, ny, rx, ry)
                opd = md(ox, oy, rx, ry)
                # Prefer resources where we are closer than the opponent, but also keep my distance low.
                t = (opd - myd) * 20 - myd
                if t > best_t:
                    best_t = t

            # Small tie-break: keep away from opponent slightly to reduce contest collisions.
            opp_d = md(nx, ny, ox, oy)
            score = best_t + opp_d * 0.1
            if score > best_score:
                best_score = score
                best_move = [dx0, dy0]
        return best_move

    # No visible resources: drift toward center while keeping distance from opponent.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            continue
        center_d = md(nx, ny, cx, cy)
        opp_d = md(nx, ny, ox, oy)
        score = opp_d * 2 - center_d * 0.5
        if score > best_score:
            best_score = score
            best_move = [dx0, dy0]
    return best_move