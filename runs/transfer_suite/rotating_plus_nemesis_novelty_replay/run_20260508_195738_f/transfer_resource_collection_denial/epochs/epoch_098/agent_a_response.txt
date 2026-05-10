def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best = None
        ti = int(observation.get("turn_index", 0) or 0)
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we reach earlier
            dist_adv = -(abs(rx - ox) + abs(ry - oy))  # further from opponent is better
            collect_race = lead * 100 + dist_adv * 2
            # tie-breaker deterministic
            score = (collect_race, lead > 0, -ds, ((rx + 3 * ry + ti) & 3) - 1, -cheb(ox, oy, sx, sy))
            if best is None or score > best[0]:
                best = (score, (rx, ry), ds)
        tx, ty = best[1]
    else:
        ti = int(observation.get("turn_index", 0) or 0)
        tx, ty = (0, 0) if ((sx + sy + ox + oy + ti) & 1) == 0 else (w - 1, h - 1)

    desired = []
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)
    desired.append((dx0, dy0))

    # deterministic fallback: prefer axis alignment then diagonal
    if dx0 == 0 and dy0 != 0:
        desired += [(1, 0), (-1, 0), (0, dy0)]
    elif dy0 == 0 and dx0 != 0:
        desired += [(0, 1), (0, -1), (dx0, 0)]
    else:
        desired += [(dx0, dy0), (dx0, 0), (0, dy0)]

    def valid(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return False
        return (nx, ny) not in obstacles

    # choose best move that heads toward target while avoiding obstacles
    best_move = (0, 0)
    best_key = None
    for dx, dy in desired + moves:
        if (dx, dy) not in desired and (dx, dy) not in moves:
            continue
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        # small preference to maintain advantage vs opponent
        d_opp_after = cheb(nx, ny, ox, oy)
        d_self = cheb(nx, ny, tx, ty)
        do_to_t = cheb(ox, oy, tx, ty)
        lead_after = do_to_t - d_self
        key = (lead_after, -d_to_t, -abs(d_opp_after), 0 if (dx, dy) == (0, 0) else -1)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move