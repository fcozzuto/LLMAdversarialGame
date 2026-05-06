def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in neigh:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            v = cheb(nx, ny, ox, oy) - (0 if nx == ox else 0) - 0.001*(abs(nx-ox)+abs(ny-oy))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Find best resource by "advantage" while biasing away from opponent's sweep pattern (same row).
        local_best = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            if my_d == 0:
                adv = 1e9
            else:
                adv = (opp_d - my_d) * 3.0 - my_d * 0.2

            # Penalize targets on the opponent's current row to reduce contention for sweep-row behavior.
            if ry == oy:
                adv -= 4.0
            # Mild bias to move to resources not aligned with opponent.
            if rx == ox:
                adv -= 1.0

            # Prefer slightly "progress" away from opponent to keep lanes separated.
            adv += 0.05 * (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))

            # Deterministic tie-break: prefer lower y then lower x when values equal.
            if adv > local_best or (adv == local_best and (ry, rx) < (best_ty, best_tx)):
                local_best = adv
                best_ty, best_tx = ry, rx

        if local_best > best_val:
            best_val = local_best
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]