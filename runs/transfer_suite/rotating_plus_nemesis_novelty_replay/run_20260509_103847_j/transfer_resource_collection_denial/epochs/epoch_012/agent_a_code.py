def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Pick target to minimize (our_dist - opp_dist): i.e., prefer states where we are closer.
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Small sd-od is good; break ties by closer sd then by coordinates for determinism
        key = (sd - od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    dirs2 = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]
    def free_neighbors(x, y):
        cnt = 0
        for dx, dy in dirs2:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                cnt += 1
        return cnt

    # Choose move that best improves relative distance to target, with a slight mobility bonus.
    best_m = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = man(nx, ny, rx, ry)
        od2 = man(ox, oy, rx, ry)
        rel = sd2 - od2  # smaller is better
        collect = 0 if (nx, ny) in resources else 1  # prefer landing on a resource (collect => 0)
        key = (rel, collect, sd2, -free_neighbors(nx, ny), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_m = [dx, dy]
    return best_m