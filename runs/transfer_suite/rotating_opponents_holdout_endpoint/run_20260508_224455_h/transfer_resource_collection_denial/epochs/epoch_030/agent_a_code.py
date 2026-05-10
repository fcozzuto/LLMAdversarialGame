def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_target():
        if not resources:
            return None
        me = (sx, sy)
        opp = (ox, oy)
        best = None
        best_val = None
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in obstacles:
                continue
            dm = dist(me, (rx, ry))
            do = dist(opp, (rx, ry))
            # Prefer resources where we are at least competitive; tie-break by smaller dm.
            val = (0 if dm <= do else 1, dm, -do, rx * 97 + ry * 7)
            if best is None or val < best_val:
                best_val = val
                best = (rx, ry)
        return best if best is not None else resources[0]

    target = best_target()
    if target is None:
        return [0, 0]

    # One-step lookahead: move that improves my distance to target; add pressure if it also worsens opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d = dist((nx, ny), target)
        opp_d = dist((ox, oy), target)
        # small bonus for moving toward opponent when my target is already fairly close
        chase_bonus = 0
        if dist((nx, ny), (ox, oy)) <= dist((sx, sy), (ox, oy)):
            chase_bonus = -0.05 * dist((nx, ny), (ox, oy))
        score = (my_d, -((opp_d - my_d)), chase_bonus, dx * 3 + dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]