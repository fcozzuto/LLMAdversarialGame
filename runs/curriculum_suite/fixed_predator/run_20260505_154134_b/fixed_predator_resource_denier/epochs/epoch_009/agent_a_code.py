def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 if d1 > d2 else d2

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    best_tie = None

    # Deterministic preference order for ties: towards opponent if resource situation is unclear.
    def tie_key(nx, ny):
        # smaller cheb to opponent is better; then closer to center to reduce predictability
        opp = cheb(nx, ny, ox, oy)
        cx = w // 2
        cy = h // 2
        center = cheb(nx, ny, cx, cy)
        return (opp, center)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            local_best = -10**18
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # If we are closer (sd<=od), strongly prioritize; else prioritize resources where we can catch up (od-sd still high).
                # Also add slight tie-break by preferring nearer resources when the relative term is similar.
                val = (od - sd) * 1000 - sd
                if val > local_best:
                    local_best = val
            val = local_best
        else:
            # No resources: head to deny by moving closer to opponent.
            val = -cheb(nx, ny, ox, oy) * 1000

        # Encourage staying near current good region: small penalty for moving away from opponent when resources exist.
        if resources:
            cur_diff = (cheb(sx, sy, ox, oy) - cheb(nx, ny, ox, oy))
            val += cur_diff

        tk = tie_key(nx, ny)
        if val > best_val or (val == best_val and (best_tie is None or tk < best_tie)):
            best_val = val
            best_move = (dx, dy)
            best_tie = tk

    return [best_move[0], best_move[1]]