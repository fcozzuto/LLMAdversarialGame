def choose_move(observation):
    env = observation.get("environment_name", "resource_collection")
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs_set = set((x, y) for x, y in obstacles)
    resources = observation.get("resources") or []

    if env == "pursuit_evasion":
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    if env == "territory_control":
        targets = observation.get("unclaimed_cells") or observation.get("opponent_territory") or []
        if not targets:
            return [0, 0]
        tx, ty = min(targets, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # resource_collection
    if not resources:
        # drift to center-ish while staying obstacle-safe
        target = (gw // 2, gh // 2)
    else:
        # choose a resource we can beat (prefer smallest (our_dist-opp_dist, our_dist))
        def score(p):
            px, py = p
            d1 = abs(px - sx) + abs(py - sy)
            d2 = abs(px - ox) + abs(py - oy)
            return (d1 - d2, d1, px, py)
        target = min(resources, key=score)

    tx, ty = target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    best = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, 0, gw - 1), clamp(sy + dy, 0, gh - 1)
        if (nx, ny) in obs_set:
            continue
        # favor moves that reduce our distance; small tie-break toward intercepting nearer than opponent
        our_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - nx) + abs(ty - ny)  # placeholder equal; use opponent position for relative pressure
        opp_d = abs(tx - ox) + abs(ty - oy)
        rel = our_d - opp_d
        # deterministic tie-break: prefer lower (rel, our_d) then lexicographic dx,dy
        cand = (rel, our_d, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or cand < best[0]:
            best = (cand, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]