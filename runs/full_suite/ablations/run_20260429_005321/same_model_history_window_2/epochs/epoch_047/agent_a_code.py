def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)  # maximize distance from opponent
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Score move by exploiting "resource race" advantages against the opponent.
    # Prefer moves that make us strictly closer to some resource than the opponent, and
    # if none, go to the nearest resource while increasing distance from opponent.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        our_dmin = 10**9
        opp_dmin = 10**9
        best_adv = -10**9  # max(opp_dist - our_dist) over resources
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            if our_d < our_dmin:
                our_dmin = our_d
            if opp_d < opp_dmin:
                opp_dmin = opp_d
            adv = opp_d - our_d
            if adv > best_adv:
                best_adv = adv

        # If we have a race advantage, weight it heavily; otherwise, seek nearest resource.
        opp_dist_now = cheb(nx, ny, ox, oy)
        score = 0
        if best_adv > 0:
            score = 1000 * best_adv - 3 * our_dmin + 0.1 * opp_dist_now
        else:
            score = -10 * our_dmin + 4 * opp_dist_now - 0.5 * opp_dmin

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]