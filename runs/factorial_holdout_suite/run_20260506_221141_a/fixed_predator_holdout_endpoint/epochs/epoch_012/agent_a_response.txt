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
    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_key = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        best_adv = -10**9
        self_best_dist = 10**9
        opp_better = 0
        opp_tie = 0

        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < self_best_dist):
                best_adv = adv
                self_best_dist = sd
            if od < sd:
                opp_better += 1
            elif od == sd:
                opp_tie += 1

        # Prefer larger advantage, then fewer resources where opponent is strictly closer,
        # then fewer ties, then closer to the most-favored resource.
        key = (-best_adv, opp_better, opp_tie, self_best_dist, abs(nx - ox) + abs(ny - oy))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]