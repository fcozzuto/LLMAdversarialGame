def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = -10**18

    if resources:
        res_set = set(tuple(r) for r in resources)
    else:
        res_set = set()

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # If we're on a resource, prefer not to waste a move away.
        on_res = 1 if (nx, ny) in res_set else 0

        # Find the best "reach first" advantage across resources.
        best_adv = -10**9
        nearest_d = 10**9
        for rx, ry in res_set if resources else []:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds
            if adv > best_adv:
                best_adv = adv
            if ds < nearest_d:
                nearest_d = ds

        # If no resources listed (edge case), just move towards center.
        if not resources:
            nearest_d = (nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2
            best_adv = 0

        # Score: maximize reach-first advantage, then slightly minimize distance to nearest resource.
        score = best_adv + 1000 * on_res - 0.01 * nearest_d

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]