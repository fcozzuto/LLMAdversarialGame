def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dxdy = (0, 0)
    best_val = -10**18

    # Choose a "target" resource where we are (relatively) closer than the opponent.
    # If none, we still head toward the nearest resource.
    def target_score(px, py, rx, ry):
        ds = cheb(px, py, rx, ry)
        do = cheb(ox, oy, rx, ry)
        return (do - ds)  # higher is better

    if resources:
        # Precompute preferred target for each move by our immediate potential.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            # Find best target advantage from this candidate position
            best_adv = -10**18
            best_d = 10**9
            for rx, ry in resources:
                adv = cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry)
                d = cheb(nx, ny, rx, ry)
                if adv > best_adv or (adv == best_adv and d < best_d):
                    best_adv = adv
                    best_d = d
            # If opponent is very close, slightly prioritize moving away while still advancing.
            danger = 2.0 if d_opp <= 1 else 0.0
            val = best_adv * 10.0 - best_d - danger * (3.0 - d_opp)
            # Small deterministic tie-breaker to avoid oscillation.
            val += -0.01 * (dx * dx + dy * dy)
            if val > best_val:
                best_val = val
                best_dxdy = (dx, dy)
    else:
        # No resources: move to maximize distance from opponent.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            val = d_opp - 0.01 * (dx * dx + dy * dy)
            if val > best_val:
                best_val = val
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]