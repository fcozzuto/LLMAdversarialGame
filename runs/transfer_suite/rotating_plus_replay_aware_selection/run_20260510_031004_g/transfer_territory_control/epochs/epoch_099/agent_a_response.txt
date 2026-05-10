def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]

    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # immediate gain estimate under territory flipping on entry
        if (nx, ny) in opp_terr:
            gain = 1.2
        elif (nx, ny) in unclaimed:
            gain = 1.0
        elif (nx, ny) in self_terr:
            gain = 0.15
        else:
            gain = 0.2

        # contest pressure / counterclaim risk
        cheb_to_opp = max(abs(nx - ox), abs(ny - oy))
        adj_risk = 0.55 if cheb_to_opp == 1 else (0.2 if cheb_to_opp == 2 else 0.0)
        # staying close to opponent while taking their cells is riskier
        if (nx, ny) in opp_terr:
            adj_risk += 0.25 / (1 + cheb_to_opp)

        # prefer occupying closer to center and slightly away from being trapped
        center = abs(nx - cx) + abs(ny - cy)
        center_score = -0.05 * center

        # keep some distance control: move toward cells farther from opponent (reduces immediate counterclaim)
        opp_dist = dist((nx, ny), (ox, oy))
        opp_score = 0.03 * opp_dist

        score = 2.0 * gain - adj_risk + center_score + opp_score

        if best is None or score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]