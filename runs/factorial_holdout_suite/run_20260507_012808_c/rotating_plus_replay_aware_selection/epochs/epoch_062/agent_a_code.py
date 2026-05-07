def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dcheb(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    res_list = [tuple(r) for r in resources]
    best_move = (0, 0)
    best_key = (-10**18, 10**9, 10**9)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose our best resource to race for; prioritize winning the race.
        # Key: (max_advantage, then we minimize our distance, then maximize opponent distance)
        max_adv = -10**18
        best_ds = 10**9
        best_do = -1
        for rx, ry in res_list:
            ds = dcheb(nx, ny, rx, ry)
            do = dcheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > max_adv or (adv == max_adv and (ds < best_ds or (ds == best_ds and do > best_do))):
                max_adv, best_ds, best_do = adv, ds, do

        # If no positive race, still try to reduce our distance to the best "contested" resource
        # while keeping opponent farther.
        key = (max_adv, best_ds, -best_do)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]