def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # When empty, just head to center while avoiding obstacles.
    if not resources:
        tx, ty = w // 2, h // 2
        for dx0, dy0 in deltas:
            nx, ny = x + dx0, y + dy0
            if not inb(nx, ny):
                continue
            if (nx == tx and ny == ty) or (dist(nx, ny, tx, ty) < dist(x, y, tx, ty)):
                return [dx0, dy0]
        return [0, 0]

    best = None
    best_key = None

    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            continue

        # Evaluate best target for this successor: prefer targets we can reach sooner.
        succ_to_opp = dist(nx, ny, ox, oy)
        best_adv = -10**9
        best_my_d = 10**9

        for rx, ry in resources:
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            adv = opp_d - my_d  # positive means we are closer
            # If we land on a resource, ensure taking it strongly.
            if nx == rx and ny == ry:
                adv += 1000
                my_d = 0
            if adv > best_adv or (adv == best_adv and my_d < best_my_d):
                best_adv = adv
                best_my_d = my_d

        # Heuristic key: maximize advantage, then minimize our distance to that target,
        # then (slightly) reduce opponent proximity to avoid being "shadowed".
        key = (best_adv, -best_my_d, -succ_to_opp)

        # Deterministic tie-break: earlier move in deltas wins.
        if best_key is None or key > best_key:
            best_key = key
            best = [dx0, dy0]

    if best is None:
        return [0, 0]
    return best