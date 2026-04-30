def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    # If opponent is closer to a resource, we "shadow": move to reduce our distance to the best remaining contested resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate next position: maximize the best achievable "advantage" among resources, with a small preference for safety.
        best_adv = -10**9
        best_my_d = 10**9
        best_block = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive => we can arrive no later than opponent
            if adv > best_adv or (adv == best_adv and (myd < best_my_d or (myd == best_my_d and (rx, ry) < (best_block, best_block)))):
                best_adv = adv
                best_my_d = myd

            # "Blocking" proxy: if moving closer to a resource also moves us toward the zone near it.
            block = -myd - (abs(rx - ox) + abs(ry - oy)) * 0.01
            if block > best_block:
                best_block = block

        # Secondary preference: avoid corners/edges only slightly; keep deterministic tie-break by coordinates.
        safety = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        key = (-(best_adv), best_my_d, -best_block, -safety, nx, ny, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]