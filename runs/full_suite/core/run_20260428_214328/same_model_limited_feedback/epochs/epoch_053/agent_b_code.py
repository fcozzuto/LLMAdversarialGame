def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)
    resources = observation.get("resources", [])

    deltas = [
        [0, 0], [1, 0], [-1, 0], [0, 1], [0, -1],
        [1, 1], [1, -1], [-1, 1], [-1, -1]
    ]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    opp_pos = (ox, oy)

    best = None
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs_set:
            continue

        new_pos = (nx, ny)
        if not resources:
            score = dist(new_pos, opp_pos)  # just keep away
        else:
            ds_near = 10**9
            winnable = -10**9
            for rx, ry in resources:
                res = (rx, ry)
                ds = dist(new_pos, res)
                do = dist(opp_pos, res)
                if ds < ds_near:
                    ds_near = ds
                if ds <= do:
                    # prefer resources we can match/beat; closer is better
                    cand = (do - ds + 1) / (ds + 1)
                    if cand > winnable:
                        winnable = cand

            if winnable < 0:
                score = -ds_near
            else:
                score = 1000 * winnable - ds_near

            # anti-collision / control: keep farther from opponent
            score += 0.75 * dist(new_pos, opp_pos)

            # slight preference to move (avoid stalling unless already best)
            if dx == 0 and dy == 0:
                score -= 0.1

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]