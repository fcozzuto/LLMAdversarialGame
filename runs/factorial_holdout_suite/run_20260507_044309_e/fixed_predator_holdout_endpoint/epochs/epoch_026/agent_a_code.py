def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = [0, 0]
    best_key = (-10**18, 10**18)

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                key = (-10**18, 10**18)
            else:
                max_adv = -10**18
                best_dist = 10**18
                for rx, ry in resources:
                    sd = man(nx, ny, rx, ry)
                    od = man(ox, oy, rx, ry)
                    adv = od - sd
                    if adv > max_adv or (adv == max_adv and sd < best_dist):
                        max_adv = adv
                        best_dist = sd
                key = (max_adv, best_dist)
            if key > best_key:
                best_key = key
                best = [dx, dy]

    return best