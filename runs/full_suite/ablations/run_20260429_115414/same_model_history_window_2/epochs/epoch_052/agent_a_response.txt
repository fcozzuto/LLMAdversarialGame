def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_score = -10**18

    # If no visible resources, drift toward center to regain options.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                continue
            score = -cheb(nx, ny, tx, ty) - 0.01 * cheb(nx, ny, ox, oy)
            if score > best_score:
                best_score, best_move = score, [dx, dy]
        return best_move

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        # Small obstacle-repulsion: prefer moves with fewer adjacent blocked cells.
        adj_blocked = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if 0 <= xx < w and 0 <= yy < h and (xx, yy) in blocked:
                    adj_blocked += 1

        # Dominance over opponent on the best available target.
        best_target_score = -10**18
        for tx, ty in resources:
            d_me = cheb(nx, ny, tx, ty)
            d_op = cheb(ox, oy, tx, ty)
            # Main: how much earlier we can arrive than the opponent.
            # Secondary: absolute closeness to that resource.
            margin = d_op - d_me  # positive is good
            target_score = 1000 * margin - 10 * d_me
            # Slightly prefer targets that are farther from opponent (to reduce their alternatives).
            target_score += -0.5 * max(0, d_op - d_me)
            if target_score > best_target_score:
                best_target_score = target_score

        # Also keep distance from opponent a bit unless it helps dominance.
        score = best_target_score + 3 * cheb(nx, ny, ox, oy) - 5 * adj_blocked
        # Tie-break deterministically: prefer staying closer to our current position slightly.
        score -= 0.01 * (abs(dx) + abs(dy))

        if score > best_score:
            best_score, best_move = score, [dx, dy]

    return best_move