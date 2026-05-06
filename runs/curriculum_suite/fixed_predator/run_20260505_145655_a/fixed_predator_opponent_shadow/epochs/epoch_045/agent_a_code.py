def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(nx, ny): 
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_adv_from(px, py):
        if not resources:
            return (0, -man(px, py, ox, oy))
        best = None
        for rx, ry in resources:
            d_me = man(px, py, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Prefer cells/resources where we'd arrive earlier or at least swing lead
            lead = d_opp - d_me
            val = (lead, -d_me, -d_opp, rx, ry)
            if best is None or val > best:
                best = val
        return best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Small deterministic bias: when multiple moves tie, prefer not moving backwards vs opponent
    opp_vec = (ox - x, oy - y)
    def back_pen(nx, ny):
        vx, vy = nx - x, ny - y
        return 0 if (vx * opp_vec[0] + vy * opp_vec[1]) >= 0 else 1

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        adv = best_adv_from(nx, ny)
        if resources:
            # additional: discourage moving toward opponent when equal lead
            d_opp_next = man(nx, ny, ox, oy)
            d_me_next = man(nx, ny, x, y)
            score = (adv[0], adv[1], adv[2], -d_opp_next, -d_me_next, -back_pen(nx, ny))
        else:
            score = (-man(nx, ny, ox, oy), -back_pen(nx, ny))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]