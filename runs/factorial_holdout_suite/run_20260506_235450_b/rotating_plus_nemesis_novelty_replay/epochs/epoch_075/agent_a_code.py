def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            my_c = abs(nx - cx) + abs(ny - cy)
            my_to_opp = abs(nx - ox) + abs(ny - oy) if opp_exists else 0
            sc = (my_to_opp * 0.6) - my_c
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # "Resource advantage": how much closer I can be than opponent to the same resource.
        best_res = -10**18
        for r in resources:
            try:
                rx, ry = r
            except:
                continue
            if (rx, ry) in obstacles:
                continue
            my_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry) if opp_exists else 10**6
            rel_adv = (opp_d - my_d)
            # small bias toward faster collection and mild avoidance of opponent interception
            my_to_opp_next = abs(nx - ox) + abs(ny - oy) if opp_exists else 0
            sc = rel_adv - 0.15 * my_d + 0.05 * my_to_opp_next - 0.02 * (abs(nx - cx) + abs(ny - cy))
            if sc > best_res:
                best_res = sc

        if best_res > best[0]:
            best = (best_res, dx, dy)
    return [best[1], best[2]]