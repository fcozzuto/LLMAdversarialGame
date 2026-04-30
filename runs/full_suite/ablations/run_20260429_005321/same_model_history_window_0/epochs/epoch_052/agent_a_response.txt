def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    cand = []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = None
        for r in resources:
            ap = dist((ox, oy), r)
            as_ = dist((sx, sy), r)
            adv = ap - as_
            key = (adv, -as_, -r[0], -r[1])
            if best is None or key > best[0]:
                best = (key, r)
        target = best[1]
    else:
        target = (w - 1 - ox, h - 1 - oy)

    best_move = (None, -10**9)
    for dx, dy, nx, ny in cand:
        d_self = dist((nx, ny), target)
        d_opp = dist((nx, ny), (ox, oy))
        opp_d_to_target = dist((ox, oy), target)
        self_d_now = dist((sx, sy), target)
        # If we're not clearly winning a target, bias toward increasing opponent's distance to it.
        anti = (d_opp - opp_d_to_target)
        score = (-d_self) + 0.05 * d_opp + 0.2 * anti + 0.001 * (observation["turn_index"] % 7)
        if score > best_move[1] or (score == best_move[1] and (dx, dy) < best_move[0]):
            best_move = ((dx, dy), score)
    dx, dy = best_move[0]
    return [int(dx), int(dy)]