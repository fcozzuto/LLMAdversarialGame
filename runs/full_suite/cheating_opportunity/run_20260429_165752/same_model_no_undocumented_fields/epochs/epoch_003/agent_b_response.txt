def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))
    if not (0 <= x < w and 0 <= y < h):
        return [0, 0]

    def inb(a, b):
        return 0 <= a < w and 0 <= b < h

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (x, y) in obstacles:
        return [0, 0]

    # If we are on a resource, grab it.
    if (x, y) in resources:
        return [0, 0]

    # Choose a target that we can plausibly reach before the opponent.
    target = None
    if resources:
        best_key = None
        for r in resources:
            ds = dist((x, y), r)
            do = dist((ox, oy), r)
            rel = ds - do  # negative means we are closer
            # Prefer strong relative advantage, then closer distance.
            key = (rel > -1, rel, ds, r[0], r[1])
            if best_key is None or key < best_key:
                best_key = key
                target = r
    else:
        target = (w // 2, h // 2)

    # Evaluate candidate moves: improve relative distance to target,
    # and secondarily reduce opponent's best stealing chance.
    best = (float("inf"), 0, 0)
    best_move = (0, 0)
    tx, ty = target
    cur_ds = dist((x, y), target)
    cur_do = dist((ox, oy), target)

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        ns = dist((nx, ny), target)
        # If we move away from target a lot, discourage.
        move_score = (ns - cur_ds)

        # Opponent stealing pressure: how close opponent would be to our target after we move.
        # (Opponent likely continues towards the nearest resource; approximate by comparing to same target.)
        opp_score = dist((ox, oy), target) - cur_do  # usually 0, but keep structure

        # If target is blocked/near, add a small term towards safer advancement: prefer reducing both axes movement.
        safety = abs(nx - tx) + abs(ny - ty)
        key = (ns - (cur_do - 0.15), abs(move_score), safety, dx, dy, opp_score)

        if key < best:
            best = key
            best_move = (dx, dy)

    # If best is staying still but there exists a valid move that reduces our distance, take it.
    if best_move == (0, 0) and resources:
        improved = None
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            ns = dist((nx, ny), target)
            if ns < cur_ds:
                improved = (dx, dy)
                break
        if improved is not None:
            return [improved[0], improved[1]]

    return [best_move[0], best_move[1]]