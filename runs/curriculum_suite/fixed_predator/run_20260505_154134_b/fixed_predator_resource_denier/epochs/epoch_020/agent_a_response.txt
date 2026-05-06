def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    remaining = observation.get("remaining_resource_count", len(resources))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def choose_target():
        if not resources:
            return (ox, oy)
        # Prefer resources where we can arrive earlier than opponent (interference),
        # but fall back to closest resource if no positive advantage exists.
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            # tie-break: smaller ds, then larger remaining "pressure" (earlier pickup)
            val = (adv, -ds, -(rx + ry))
            if best is None or val > best[0]:
                best = (val, (rx, ry))
        return best[1] if best is not None else (ox, oy)

    target = choose_target()
    # If resources are nearly gone, switch to direct contest (resource denial -> chase)
    chase = (remaining <= 3 and not resources) or (remaining <= 2)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if chase and resources:
            # Chase opponent position to deny access/tempo
            score = -cheb(nx, ny, ox, oy)
        else:
            # Choose move that maximizes our arrival advantage for the best contestable resource
            score = -10**18
            if resources:
                for rx, ry in resources:
                    if (rx, ry) in obstacles:
                        continue
                    ds = cheb(nx, ny, rx, ry)
                    do = cheb(ox, oy, rx, ry)
                    adv = do - ds
                    val = (adv * 1000) - ds  # primary: beat opponent, secondary: be close
                    if val > score:
                        score = val
            if score == -10**18:
                # No reachable resources (all blocked): just move toward target/opponent
                score = -cheb(nx, ny, target[0], target[1])

        # mild obstacle-safe bias: prefer staying away from obstacles by distance
        if obstacles:
            min_ob_d = 99
            for oxp, oyp in obstacles:
                d = cheb(nx, ny, oxp, oyp)
                if d < min_ob_d:
                    min_ob_d = d
            score += min_ob_d * 0.01

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]