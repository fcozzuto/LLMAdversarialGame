def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_toward(tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return dx, dy

    # No resources: break symmetry and avoid being corner-followed
    if not resources:
        best = (0, 0)
        bestv = -10**18
        tx, ty = w - 1, h - 1
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            v = d_opp * 1000 - (abs(nx - tx) + abs(ny - ty))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # With resources: win access if possible; otherwise deny the most valuable one.
    best = (0, 0)
    bestv = -10**18
    tx_far, ty_far = w - 1, h - 1
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        local = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            cur = 0
            if myd == 0:
                cur += 20000
            # If we're closer than opponent, push hard; else deny based on how close opponent is.
            if myd < opd:
                cur += (opd - myd) * 2200 + (15 - myd) * 20
            elif myd == opd:
                cur += 200 + (15 - myd)
            else:
                # Deny: move toward resources where opponent has an advantage.
                cur += - (myd - opd) * 180 + max(0, 14 - myd) * 6 + max(0, 18 - opd) * 4

            # Mild preference to reduce opponent distance while staying near resources
            cur += (cheb(nx, ny, ox, oy) * -0.5)

            # Keep some deterministic pressure toward upper-left if still competitive (helps diversification)
            cur += -0.1 * (abs(nx - 0) + abs(ny - 0))

            # Tie-breaker alignment: prefer moving closer to the far corner after choices
            cur += -0.05 * (abs(nx - tx_far) + abs(ny - ty_far))
            if cur > local:
                local = cur

        if local > bestv or (local == bestv and (dx, dy) < best):
            bestv = local
            best = (dx, dy)

    return [best[0], best[1]]