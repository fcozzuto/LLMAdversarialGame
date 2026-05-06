def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            r = (p[0], p[1])
            if r not in obstacles:
                resources.append(r)
    if not resources:
        return [0, 0]

    resources.sort()
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Favors moves that make us closer to contested resources than the opponent,
    # with a mild preference for short own distance.
    best_dx, best_dy = 0, 0
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = -0.25 * man(nx, ny, sx, sy)  # small penalty for moving away (prevents jitter)

        # Consider up to 6 closest resources to keep it fast and stable.
        near = []
        for rx, ry in resources:
            near.append((man(nx, ny, rx, ry), man(ox, oy, rx, ry), rx, ry))
        near.sort()
        near = near[:6]

        for ds, do, rx, ry in near:
            # If we are closer than opponent, reward strongly; if farther, penalize a bit.
            diff = do - ds
            contest = 2.2 * diff
            close_bonus = 3.0 / (1 + ds)
            v += contest + close_bonus

            # If opponent can reach in the same step or sooner, discourage unless we are also close.
            if do <= ds:
                v -= 0.8 / (1 + ds)

            # If we can land on a resource now, prioritize deterministically.
            if ds == 0:
                v += 50.0

        if v > best_val or (v == best_val and (dx, dy) == moves[0]):
            best_val = v
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]