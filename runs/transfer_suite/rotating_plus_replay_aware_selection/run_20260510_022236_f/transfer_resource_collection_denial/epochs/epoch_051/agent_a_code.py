def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b, x, y):
        return abs(a - x) + abs(b - y)

    def adj_obs_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in obs:
                    pen += 1
        return pen

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Choose based on best target from each candidate move (compete: higher advantage first)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        step_pen = adj_obs_pen(nx, ny)
        best_adv_for_move = -10**18
        best_tdist = 10**18
        best_tie = (0, 0)
        for tx, ty in res:
            sd = dist(nx, ny, tx, ty)
            od = dist(ox, oy, tx, ty)
            adv = od - sd  # positive means we are closer/equal
            # slight preference to faster collection (lower sd), and to staying away from obstacles
            val = adv * 1000 - sd - step_pen * 3
            if val > best_adv_for_move or (val == best_adv_for_move and (sd, tx, ty) < (best_tdist, best_tie[0], best_tie[1])):
                best_adv_for_move = val
                best_tdist = sd
                best_tie = (tx, ty)
        # Prefer immediate resource pickup if adjacent by deterministic tie-breaking
        if (nx, ny) in res:
            best_adv_for_move += 10**7
        if best_adv_for_move > best_val:
            best_val = best_adv_for_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]