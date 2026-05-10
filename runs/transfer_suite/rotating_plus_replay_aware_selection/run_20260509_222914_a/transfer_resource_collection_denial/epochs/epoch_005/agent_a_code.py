def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):  # Chebyshev for diagonal-friendly planning
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Pick a target that we can plausibly arrive first: maximize (opp_dist - self_dist),
        # with a secondary preference for closer self distance.
        best = None
        best_key = None
        for rx, ry in resources:
            sd = dist(x, y, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd
            key = (-(adv), sd, rx, ry)  # smallest key wins
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    nx0, ny0 = x, y
    # Deterministic tie-break order in deltas list.
    if (x, y) in obstacles:
        # If somehow inside obstacle, attempt first valid move.
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def next_valid(dx, dy):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return nx, ny
        return None

    # Strongly prefer stepping onto a resource; otherwise step that reduces self distance to target,
    # but also tries to avoid stepping into "giving" the opponent an immediate capture.
    resources_set = set((p[0], p[1]) for p in resources)
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nxt = next_valid(dx, dy)
        if nxt is None:
            continue
        nx, ny = nxt
        if resources and (nx, ny) in resources_set:
            return [dx, dy]

        sd = dist(nx, ny, tx, ty)
        cur_sd = dist(x, y, tx, ty)
        od = dist(ox, oy, tx, ty)

        # Estimate whether opponent can capture quickly at/near our next position if it were a resource.
        # If they are very close to any resource that is also near us, we slightly discourage.
        opp_cap = 0
        if resources:
            for rx, ry in resources:
                if dist(nx, ny, rx, ry) <= 1:
                    opp_cap = min(opp_cap or 10**9, dist(ox, oy, rx, ry))
        opp_pen = 0 if opp_cap == 0 else (1 if opp_cap <= 1 else 0)

        val = (sd, - (cur_sd - sd), od, opp_pen, nx, ny)  # minimize sd and discourage giving
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]