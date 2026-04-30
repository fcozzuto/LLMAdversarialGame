def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose a target resource where we are relatively closer than the opponent.
    resources.sort(key=lambda r: (r[0] * 31 + r[1] * 17, r[0], r[1]))
    best_r = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        adv = opp_d - our_d
        if adv > best_adv:
            best_adv = adv
            best_r = (rx, ry)
        elif adv == best_adv:
            if our_d < cheb(sx, sy, best_r[0], best_r[1]):
                best_r = (rx, ry)

    tx, ty = best_r
    opp_close = cheb(ox, oy, tx, ty) <= 1

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_d = cheb(nx, ny, tx, ty)
        opp_d_after = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        # Primary: get closer to target. Secondary: keep opponent farther from taking it.
        score = -our_d + 0.35 * opp_d_after
        # If opponent is very close to the target, shift to "deny" by increasing opp distance in our own perspective.
        if opp_close:
            # Encourage moving away from the target (or at least not closer to it).
            score += 0.9 * cheb(nx, ny, ox, oy) - 0.6 * our_d
        # Small tie-breaker: prefer not stepping into "worse" centrality (keep it deterministic and mild).
        score += -0.01 * cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]