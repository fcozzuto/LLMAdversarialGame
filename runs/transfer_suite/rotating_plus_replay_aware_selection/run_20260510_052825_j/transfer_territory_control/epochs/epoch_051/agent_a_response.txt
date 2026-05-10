def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    # Pick a deterministic target among promising unclaimed cells
    candidates = []
    for tx, ty in unclaimed:
        if (tx, ty) in selfT or (tx, ty) in oppT:
            continue
        d_opp = man(tx, ty, ox, oy)
        d_us = man(tx, ty, x, y)
        # Prefer far from opponent (safer expansion) and not too far from us (reachable)
        candidates.append((-(d_opp) + 0.35 * d_us, tx, ty, d_opp, d_us))
    candidates.sort()
    if candidates:
        _, tx, ty, _, _ = candidates[0]
    else:
        # No unclaimed: aim to intersect near opponent territory
        # Find closest opponent territory cell by manhattan
        if oppT:
            best = None
            for px, py in oppT:
                d = man(px, py, x, y)
                if best is None or d < best[0] or (d == best[0] and (px, py) < best[1]):
                    best = (d, (px, py))
            tx, ty = best[1]
        else:
            return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            sc = -10**9
        else:
            d_to_target = man(nx, ny, tx, ty)
            d_to_opp = man(nx, ny, ox, oy)
            sc = 0
            if (nx, ny) in oppT:
                sc += 10  # likely immediate flipping/control gain
            elif (nx, ny) in unclaimed:
                sc += 6
            elif (nx, ny) in selfT:
                sc += 2
            # Progress toward target
            sc += 3 - d_to_target * 0.6
            # Avoid getting too close unless flipping opponent
            if (nx, ny) not in oppT and d_to_opp <= 1:
                sc -= 6
            # Prefer staying aligned with our starting corner (helps stability)
            if x <= 1 and y <= 1:
                sc += (nx + ny) * 0.01
            elif x >= w - 2 and y >= h - 2:
                sc += ((w - 1 - nx) + (h - 1 - ny)) * 0.01
            # Tiny deterministic tie-break
            sc += -(abs(dx) + abs(dy)) * 0.001
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]