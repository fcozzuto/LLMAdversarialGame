def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def king(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_key = (-10**18, -10**18, -10**18)

    for dxm in (-1, 0, 1):
        for dym in (-1, 0, 1):
            nx, ny = sx + dxm, sy + dym
            if not inside(nx, ny) or (nx, ny) in obs:
                continue

            max_adv = -10**18
            best_sd = 10**18
            best_od = -10**18
            for rx, ry in resources:
                sd = king(nx, ny, rx, ry)
                od = king(ox, oy, rx, ry)
                adv = od - sd
                if adv > max_adv or (adv == max_adv and (sd < best_sd or (sd == best_sd and od > best_od))):
                    max_adv, best_sd, best_od = adv, sd, od

            if max_adv <= 0:
                nearest_sd = 10**18
                for rx, ry in resources:
                    nearest_sd = min(nearest_sd, king(nx, ny, rx, ry))
                key = (max_adv, -nearest_sd, -10**9)
            else:
                key = (max_adv, -best_sd, best_od)

            if key > best_key:
                best_key = key
                best_move = [dxm, dym]

    if best_move == [0, 0]:
        for dxm in (-1, 0, 1):
            for dym in (-1, 0, 1):
                nx, ny = sx + dxm, sy + dym
                if inside(nx, ny) and (nx, ny) not in obs:
                    return [dxm, dym]
    return best_move