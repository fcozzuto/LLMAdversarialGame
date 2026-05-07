def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    if not resources:
        return [0, 0]

    obst = {(int(a), int(b)) for a, b in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        best_adv = None
        opp_better_count = 0
        self_closest = 10**9
        tie_mass = 0

        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            if best_adv is None or adv > best_adv or (adv == best_adv and sd < self_closest):
                best_adv = adv
            if od <= sd:
                opp_better_count += 1
                if od == sd:
                    tie_mass += 1
            if sd < self_closest:
                self_closest = sd

        key = (-best_adv, opp_better_count, tie_mass, self_closest, nx, ny)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]