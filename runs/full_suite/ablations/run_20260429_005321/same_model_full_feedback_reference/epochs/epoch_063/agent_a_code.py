def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # If resources exist, move to a cell that maximizes advantage over opponent for the best resource.
    best = (0, 0)
    bestv = -10**18

    if resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue

            score = 0
            anypos = False
            closest_adv = -10**18
            # Evaluate resources: prefer those where we are closer than opponent, and nearer in absolute terms.
            for rx, ry in resources:
                ds = dist2(nx, ny, rx, ry)
                do = dist2(ox, oy, rx, ry)
                # Advantage: positive when we are closer; strong when do is much larger.
                adv = (do - ds)
                # Tie-breaker: prefer smaller ds overall.
                val = adv * 1000 - ds
                if val > closest_adv:
                    closest_adv = val
                if adv > 0:
                    anypos = True
            # Encourage actually reaching a resource rather than only denying.
            # Also slight pressure to get closer to opponent if no immediate winning resource.
            if anypos:
                score = closest_adv
            else:
                # No resource where we lead: pivot toward "frontier" near opponent direction while maintaining closest resource pressure.
                # Use minimal (ds - do): resources that reduce opponent's lead.
                mindiff = 10**18
                for rx, ry in resources:
                    mindiff = min(mindiff, dist2(nx, ny, rx, ry) - dist2(ox, oy, rx, ry))
                # Combine: smaller mindiff better, plus approach opponent a bit.
                score = -mindiff * 200 - dist2(nx, ny, ox, oy)

            # Deterministic final tie-break: prefer moves with smaller distance to nearest resource.
            if score > bestv:
                bestv = score
                best = (dx, dy)
            elif score == bestv:
                # tie: choose smallest dist2 to opponent (more likely to contest) then smallest dist2 to closest resource
                if dist2(nx, ny, ox, oy) < dist2(sx + best[0], sy + best[1], ox, oy):
                    best = (dx, dy)

        return [int(best[0]), int(best[1])]

    # No resources: advance deterministically toward a cell that reduces distance to opponent, avoiding obstacles.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = -dist2(nx, ny, ox, oy)  # maximize negative distance => minimize distance
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]