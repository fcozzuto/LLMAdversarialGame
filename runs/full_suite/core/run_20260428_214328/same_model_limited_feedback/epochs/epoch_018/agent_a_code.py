def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # Move toward opponent if no resources remain
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]

    best = None
    best_move = [0, 0]
    center = (w / 2.0, h / 2.0)

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            if resources:
                # Choose move that maximizes our advantage toward the best resource.
                local_best = -10**9
                local_dself = 10**9
                local_dopp = 10**9
                for r in resources:
                    dself = dist((nx, ny), r)
                    dopp = dist((ox, oy), r)
                    adv = dopp - dself
                    if adv > local_best or (adv == local_best and (dself < local_dself or (dself == local_dself and dopp < local_dopp))):
                        local_best = adv
                        local_dself = dself
                        local_dopp = dopp
                score = (local_best, -local_dself, -(abs(nx - center[0]) + abs(ny - center[1])))
            else:
                # Fallback: move toward center
                score = (0, -(abs(nx - center[0]) + abs(ny - center[1])))

            if best is None or score > best:
                best = score
                best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move