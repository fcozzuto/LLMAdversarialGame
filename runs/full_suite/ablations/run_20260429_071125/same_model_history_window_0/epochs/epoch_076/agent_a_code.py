def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    opp = (ox, oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        # Choose resource with greatest advantage (opponent farthest relative to us).
        best_r = None
        best_adv = -10**18
        for r in resources:
            r = tuple(r)
            d_me = dist((sx, sy), r)
            d_opp = dist(opp, r)
            adv = d_opp - d_me
            if adv > best_adv:
                best_adv = adv
                best_r = r
        target = best_r
    else:
        # No resources: head toward opponent to potentially block/contend.
        target = opp

    def move_valid(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    candidates = []
    for dx, dy in moves:
        if not move_valid(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        d_to_t = dist((nx, ny), target)
        d_from_opp = dist((nx, ny), opp)
        # Tie-breakers: prefer reducing distance to target; if tie, maximize separation from opponent; then deterministic order.
        candidates.append((d_to_t, -d_from_opp, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort()
    dx, dy = candidates[0][2], candidates[0][3]
    return [dx, dy]