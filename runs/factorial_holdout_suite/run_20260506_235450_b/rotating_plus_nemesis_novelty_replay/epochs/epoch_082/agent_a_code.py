def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # If no resources visible, drift to a corner-biased safe point to avoid being predictable
    if not resources:
        # Prefer moving away from opponent corner while staying close to midline
        tx = 1 if sx > (w - 1) // 2 else w - 2
        ty = 1 if sy > (h - 1) // 2 else h - 2
        if opp_exists:
            if ox > (w - 1) // 2:
                tx = 0
            else:
                tx = w - 1
            if oy > (h - 1) // 2:
                ty = 0
            else:
                ty = h - 1
        # Pick best among local moves
        best = (-10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    pass
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                sc = -(abs(nx - tx) + abs(ny - ty))
                if sc > best[0]:
                    best = (sc, dx, dy)
        return [best[1], best[2]]

    # Score resources by our advantage over opponent (resource denial pressure)
    # Aim: choose a resource where we are likely to arrive first.
    best_target = None
    best_val = -10**18
    for rx, ry in resources:
        d_self = abs(rx - sx) + abs(ry - sy)
        d_opp = abs(rx - ox) + abs(ry - oy) if opp_exists else 10**9
        # Encourage closing when we are ahead; heavily penalize when opponent is much closer.
        val = (d_opp - d_self) - 0.15 * d_self + (0.5 if (rx + ry) % 2 == (sx + sy) % 2 else 0)
        # Small deterministic tie-break toward closer resource
        val += -0.001 * d_self
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target
    # Choose a step that reduces Manhattan distance to target and stays unblocked.
    best = (-10**9, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            nd = abs(tx - nx) + abs(ty - ny)
            # Also add a small "contest" bonus if this step increases our advantage vs opponent on target
            d_self_now = abs(tx - sx) + abs(ty - sy)
            d_opp_now = abs(tx - ox) + abs(ty - oy) if opp_exists else 10**9
            d_self_after = nd
            d_opp_after = abs(tx - ox) + abs(ty - oy) if opp_exists else 10**9
            contest = (d_opp_after - d_self_after) - (d_opp_now - d_self_now)
            sc = (-nd) + 0.3 * contest
            if sc > best[0]:
                best = (sc, dx, dy)
    return [best[1], best[2]]