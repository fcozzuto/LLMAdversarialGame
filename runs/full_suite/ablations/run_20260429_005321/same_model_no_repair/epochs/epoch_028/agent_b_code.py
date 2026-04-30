def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    obs_set = set((x, y) for x, y in obstacles)
    def obs_pen(x, y):
        if (x, y) in obs_set:
            return 10**9
        p = 0
        for ex, ey in obstacles:
            d = abs(x - ex) + abs(y - ey)
            if d == 0:
                p += 1000
            elif d == 1:
                p += 20
            elif d == 2:
                p += 6
            elif d == 3:
                p += 2
        return p

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Consider only a few promising resources to keep deterministic and fast.
    r_sorted = sorted(resources, key=lambda r: (man(ox, oy, r[0], r[1]), r[0], r[1]))
    topk = 6 if len(r_sorted) >= 6 else len(r_sorted)
    resources_considered = r_sorted[:topk]

    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        p_obs = obs_pen(nx, ny)

        # Value is the best advantage we can create on our next position.
        # Advantage: (opponent distance - our distance) so larger is better.
        best_adv = -10**18
        for rx, ry in resources_considered:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            adv = d_opp - d_self
            # Small tie-break: prefer moving closer to the resource when advantage ties.
            adv -= 0.01 * d_self
            best_adv = adv if adv > best_adv else best_adv

        # Mild preference to not step adjacent to obstacles too much; already included.
        val = best_adv - p_obs
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]