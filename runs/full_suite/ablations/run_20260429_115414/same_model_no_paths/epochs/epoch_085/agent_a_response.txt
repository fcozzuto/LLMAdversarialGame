def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    best_score = -10**18

    opp_dist_now = cheb(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Safety: avoid getting too close when resources are scarce.
        safety = 2 - cheb(nx, ny, ox, oy)
        scarcity = 1 if (observation.get("remaining_resource_count") or len(resources)) <= 3 else 0
        safety_score = safety - (3 * scarcity if opp_dist_now <= 2 else 0)

        if resources:
            # Choose the resource where we can gain the most advantage (or at least contest).
            best_adv = -10**18
            for rx, ry in resources:
                my_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                # If we are not at least as close as the opponent, penalize approaching it.
                if my_d <= opp_d:
                    adv = opp_d - my_d
                else:
                    adv = (opp_d - my_d) - 2
                if adv > best_adv:
                    best_adv = adv
            # Strongly prefer maximizing advantage; lightly prefer moves that reduce distance to opponent when contested.
            score = 10 * best_adv + safety_score
        else:
            score = safety_score

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]