def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Prefer actions that create the largest "reach advantage" against any resource.
    # Tie-break: prefer smaller self distance to that chosen resource, then prefer moving (not staying).
    best_move = [0, 0]
    best_key = (-10**18, -10**18, 1)  # (adv, -selfDist, stayPenalty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        local_best_adv = -10**18
        local_best_self = 10**18
        local_best_opp = 10**18

        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer (or equal) than opponent
            if adv > local_best_adv or (adv == local_best_adv and (sd < local_best_self or (sd == local_best_self and od < local_best_opp))):
                local_best_adv, local_best_self, local_best_opp = adv, sd, od

        # Small preference to not linger when tie on advantage.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        key = (local_best_adv, -local_best_self, stay_pen)
        if key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move