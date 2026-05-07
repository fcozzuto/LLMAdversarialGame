def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh

    def legal(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not res:
        best = None
        bd = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            score = (d, -abs(dx), -abs(dy), -dx, -dy)
            if best is None or score > best:
                best, bd = score, (dx, dy)
        return [bd[0], bd[1]]

    best = None
    bd = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Choose the resource where we have the strongest "reach advantage" and minimal time.
        best_for_move = None
        for rx, ry in res:
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Advantage: positive means opponent farther from that resource than we are.
            adv = opp_d - my_d
            # Penalize moving toward a resource while letting opponent be much closer.
            # Reward smaller my_d and better separation from opponent.
            sep = man(nx, ny, ox, oy)
            score_r = (adv, -my_d, sep, -abs(dx) - abs(dy), -rx, -ry)
            if best_for_move is None or score_r > best_for_move:
                best_for_move = score_r
        if best is None or best_for_move > best:
            best, bd = best_for_move, (dx, dy)
    return [bd[0], bd[1]]