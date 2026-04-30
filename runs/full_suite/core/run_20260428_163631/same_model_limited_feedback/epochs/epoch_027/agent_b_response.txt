def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obs = set((p[0], p[1]) for p in obstacles)
    res = [ (p[0], p[1]) for p in resources if 0 <= p[0] < w and 0 <= p[1] < h and (p[0], p[1]) not in obs ]
    if not res:
        res = [(sx, sy)]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    my = (sx, sy)
    opp = (ox, oy)

    best_t = None
    best_adv = -10**9
    for r in res:
        d1 = dist(my, r)
        d2 = dist(opp, r)
        adv = d2 - d1  # I closer => larger
        if adv > best_adv or (adv == best_adv and (best_t is None or d1 < dist(my, best_t))):
            best_adv = adv
            best_t = r

    tx, ty = best_t
    best_move = [0, 0]
    best_score = None

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d_to = dist((nx, ny), (tx, ty))
        d_from_opp = dist((nx, ny), opp)
        # Primary: minimize distance to target; Secondary: maximize distance from opponent; Tertiary: deterministic order via dx,dy
        score = (d_to, -d_from_opp, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]