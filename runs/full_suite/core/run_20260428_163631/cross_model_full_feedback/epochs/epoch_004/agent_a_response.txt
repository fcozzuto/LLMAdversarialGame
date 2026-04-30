def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(r) for r in observation.get("resources", [])]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose target deterministically: maximize (opp closer advantage) but with tie-break
    target = None
    best_t = None
    for r in resources:
        if r in obstacles:
            continue
        d_me = dist((sx, sy), r)
        d_opp = dist((ox, oy), r)
        key = (d_opp - d_me, r[0], r[1])
        if best_t is None or key > best_t:
            best_t = key
            target = r

    if target is None:
        target = (w // 2, h // 2)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep in place; emulate deterministically

        d_me = dist((nx, ny), target)
        d_opp = dist((ox, oy), target)

        # Prefer getting closer than opponent, and avoid getting too close to opponent
        util = (d_opp - d_me)
        d_to_opp = dist((nx, ny), (ox, oy))
        util -= 0.25 * max(0, 6 - d_to_opp)  # slight repulsion when within range

        # Mild bias: move that reduces distance to target earlier
        d_now = dist((sx, sy), target)
        util += 0.05 * (d_now - d_me)

        if util > best_val or (util == best_val and (dx, dy) < best_move):
            best_val = util
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]