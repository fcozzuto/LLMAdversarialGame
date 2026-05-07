def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer moves that improve our chance to arrive first at some resource.
        # Advantage = opponent_distance - our_distance (bigger is better).
        move_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd

            # Encourage closeness, but heavily reward positive advantage.
            # If adv is negative, still consider it when it is our best remaining option.
            val = (adv * 1000) - sd

            # If extremely tight race, prefer whichever is nearer to us.
            if adv == 0:
                val -= 10

            if val > move_best:
                move_best = val

        # Secondary preference: reduce our distance to nearest resource overall.
        # This stabilizes movement when multiple moves have similar race values.
        nearest_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        score = move_best - nearest_self

        if score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]