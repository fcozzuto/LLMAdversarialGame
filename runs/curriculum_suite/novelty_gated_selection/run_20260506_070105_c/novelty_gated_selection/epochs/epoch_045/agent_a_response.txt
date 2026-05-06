def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def p2t(p, default):
        try:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    return (x, y)
        except Exception:
            pass
        return default

    self_pos = p2t(observation.get("self_position", None), (0, 0))
    opp_pos = p2t(observation.get("opponent_position", None), (w - 1, h - 1))
    sx, sy = self_pos
    ox, oy = opp_pos

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if tuple(r) not in obstacles]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    res = resources
    occ_opp_res = False
    # Predict opponent next by probing toward one corner (diagonal bias): towards (0,0)
    odx = -1 if ox > 0 else (1 if ox < 0 else 0)
    ody = -1 if oy > 0 else (1 if oy < 0 else 0)
    opp_next = (ox + odx, oy + ody)
    if not (0 <= opp_next[0] < w and 0 <= opp_next[1] < h) or opp_next in obstacles:
        opp_next = (ox, oy)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose move maximizing resource progress while keeping distance from opponent next.
    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_closest = min(man((nx, ny), r) for r in res)
        d_to_opp = man((nx, ny), opp_next)
        # If we can step onto a resource, prioritize heavily.
        on_resource = 1 if (nx, ny) in obstacles else 0
        sc = 1000 * (1 if (nx, ny) in res else 0) - d_to_closest + 0.15 * d_to_opp
        # Slight deterrent if moving into opponent's immediate influence
        if (nx, ny) == opp_next:
            sc -= 50
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]