def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(nx, ny, tx, ty):
        return abs(tx - nx) + abs(ty - ny)

    def target_score(tx, ty):
        d_me = man(x, y, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        return (d_opp - d_me) * 1000 - d_me

    def best_resource():
        if not resources:
            return None
        best = resources[0]
        best_s = target_score(best[0], best[1])
        for r in resources[1:]:
            s = target_score(r[0], r[1])
            if s > best_s or (s == best_s and (r[0], r[1]) < (best[0], best[1])):
                best, best_s = r, s
        return best

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    tx, ty = best_resource()[0], best_resource()[1]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def move_value(dx, dy):
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            return -10**18
        if (nx, ny) in obstacles:
            return -10**18
        # Evaluate by projected advantage to best target and ability to approach it
        d_me2 = man(nx, ny, tx, ty)
        d_opp2 = man(ox, oy, tx, ty)
        # Small tiebreak to prefer moving toward both coordinates
        return (d_opp2 - d_me2) * 1000 - d_me2 + 0.01 * (abs(tx - ox) + abs(ty - oy))

    best_m = (0, 0)
    best_v = move_value(0, 0)
    for dx, dy in moves:
        v = move_value(dx, dy)
        if v > best_v or (v == best_v and (dx, dy) < best_m):
            best_v, best_m = v, (dx, dy)

    if best_v <= -10**17:
        return [-sign(ox - x), -sign(oy - y)]
    return [best_m[0], best_m[1]]