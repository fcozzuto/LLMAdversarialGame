def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res_set.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        immediate = 1 if (nx, ny) in res_set else 0
        best_adv = -10**18
        best_d = 10**9
        best_rxry = (10**9, 10**9)

        for rx, ry in res_set:
            our_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            adv = opp_d - our_d
            # If immediate collection, heavily prefer it.
            if (nx, ny) == (rx, ry):
                adv += 10**6
            # Mildly avoid targets where opponent is already closer.
            if opp_d < our_d:
                adv -= 2

            if adv > best_adv or (adv == best_adv and (our_d < best_d or (our_d == best_d and (rx, ry) < best_rxry))):
                best_adv, best_d, best_rxry = adv, our_d, (rx, ry)

        key = (immediate, best_adv, -best_d, -best_rxry[0], -best_rxry[1])
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]