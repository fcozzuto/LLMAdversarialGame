def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def d(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    resources.sort()

    cur_best_opp = None
    best_opp_d = 10**9
    for r in resources:
        dr = d((ox, oy), r)
        if dr < best_opp_d:
            best_opp_d = dr
            cur_best_opp = r

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        my_pos = (nx, ny)
        val = 0

        # If we can collect immediately, dominate.
        if my_pos in resources:
            val += 10**6

        # Advantage over opponent: larger (d_opp - d_self) is better.
        local_best = -10**18
        for r in resources:
            ds = d(my_pos, r)
            do = d((ox, oy), r)
            diff = do - ds
            if diff > local_best:
                local_best = diff
        val += local_best * 1000

        # Tie-break: prefer reducing our distance to the best resource if opponent can't be beaten much.
        ds_closest = 10**9
        for r in resources:
            ds_closest = min(ds_closest, d(my_pos, r))
        val -= ds_closest

        # Denial when opponent is ahead globally: approach opponent's nearest resource.
        if cur_best_opp is not None:
            if d((ox, oy), cur_best_opp) < min(d((sx, sy), r) for r in resources):
                val -= d(my_pos, cur_best_opp)

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]