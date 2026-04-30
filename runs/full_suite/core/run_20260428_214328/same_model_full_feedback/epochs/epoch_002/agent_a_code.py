def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    if resources:
        best_r = None
        best_key = None
        for r in resources:
            dself = dist((sx, sy), r)
            dopp = dist((ox, oy), r)
            # prefer resources we can get first, otherwise deny by going to one opponent is near
            key = (dopp - dself, -dself, -r[0], -r[1])
            if best_key is None or key > best_key:
                best_key = key
                best_r = r
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dself = dist((nx, ny), (tx, ty))
        dropp = dist((ox, oy), (tx, ty))
        # If opponent can reach target soon, we bias toward alternative resource
        alt_penalty = 0
        if resources:
            best_alt = None
            for r in resources:
                if r == (tx, ty):
                    continue
                ds = dist((nx, ny), r)
                do = dist((ox, oy), r)
                key = (do - ds, -ds)
                if best_alt is None or key > best_alt[0]:
                    best_alt = (key, r)
            if best_alt is not None:
                best_alt_key, _ = best_alt
                alt_penalty = -best_alt_key[0]  # higher alt advantage reduces penalty
        # Heuristic: get closer, keep distance from opponent slightly, and reduce overall risk
        key = (
            -dself,
            (dropp - dist((ox, oy), (nx, ny))),  # prefer moving away from opponent less (effectively)
            alt_penalty,
            -abs(nx - sx),
            -abs(ny - sy),
            dx,
            dy,
        )
        moves.append((key, [dx, dy]))

    if not moves:
        return [0, 0]
    moves.sort(key=lambda x: x[0], reverse=True)
    return moves[0][1]