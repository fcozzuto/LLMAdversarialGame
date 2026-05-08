def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (7, 7))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                v = md(ox, oy, nx, ny) - md(sx, sy, nx, ny)
                if v > bestv:
                    bestv = v
                    best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18

    # Evaluate each move by: immediate distance advantage to the best contested resource,
    # plus a small preference to keep moving toward the current nearest resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Find best resource for us if we are to move into (nx, ny)
        best_adv = -10**18
        best_self = 10**9
        best_opp = 10**9
        for rx, ry in resources:
            d_self = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            adv = d_opp - d_self
            # Prefer larger advantage; tie-break by closer self then farther opp (deny)
            if adv > best_adv or (adv == best_adv and (d_self < best_self or (d_self == best_self and d_opp > best_opp))):
                best_adv = adv
                best_self = d_self
                best_opp = d_opp

        # Extra: prevent opponent from "cutting in" by moving toward a resource that is far for opponent
        # while still not worsening our advantage.
        v = 0
        v += best_adv * 1000
        v += (20 - best_self)  # closer is better
        v += (best_opp - 20)  # larger opp distance is better
        # Small bias: don't wander—prefer smaller step from current
        step = abs(dx) + abs(dy)
        v -= step

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]