def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []

    obs_set = {(x, y) for x, y in obstacles if 0 <= x < w and 0 <= y < h}
    un_set = {(x, y) for x, y in unclaimed if 0 <= x < w and 0 <= y < h}
    my_set = {(x, y) for x, y in my_t if 0 <= x < w and 0 <= y < h}
    op_set = {(x, y) for x, y in op_t if 0 <= x < w and 0 <= y < h}

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist_to_center(x, y): 
        dx, dy = x - cx, y - cy
        return dx*dx + dy*dy

    best = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        if (nx, ny) in my_set:
            cell = 3.0
        elif (nx, ny) in un_set:
            cell = 7.0
        elif (nx, ny) in op_set:
            cell = 9.0  # flipping enabled on entry
        else:
            cell = 1.0  # should be rare

        # Prefer heading toward center, but slightly penalize distance increases
        d0 = dist_to_center(ax, ay)
        d1 = dist_to_center(nx, ny)
        toward = (d0 - d1) * 0.6

        # Avoid stepping into "likely contested" edge: if opponent neighbors many times, prefer grabbing
        # Deterministic local count for opponent around target
        opp_n = 0
        for tx in (-1,0,1):
            for ty in (-1,0,1):
                if tx == 0 and ty == 0: 
                    continue
                px, py = nx + tx, ny + ty
                if inb(px, py) and (px, py) in op_set:
                    opp_n += 1

        score = cell + toward + opp_n * 0.25 - ((nx, ny) in op_set) * 0.05
        key = (score, -d1, -abs(nx - cx) - abs(ny - cy), -abs(dx) - abs(dy), dx, dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]