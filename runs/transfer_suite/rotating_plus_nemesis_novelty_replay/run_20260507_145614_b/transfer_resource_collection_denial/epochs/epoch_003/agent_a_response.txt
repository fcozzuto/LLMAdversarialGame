def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # Deterministic: go toward center while avoiding obstacles; if blocked, stay.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            cand = (d, dx, dy)
            if cand < best:
                best = cand
        return [best[1], best[2]] if best[0] != 10**9 else [0, 0]

    # Score a move by best resource we could be closest to vs opponent.
    # We minimize (negative advantage, our distance, opponent distance) deterministically.
    best_move = (10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        best_for_move = (10**18, 0)  # (key, which_resource_index)
        for i, (rx, ry) in enumerate(resources):
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer cells where our distance is small and our advantage over opponent is big.
            # Key uses lexicographic minimization.
            adv_key = (-(do - ds), ds, do, i)
            if adv_key < best_for_move[0] if isinstance(best_for_move[0], tuple) else False:
                pass

        # Simpler: compute minimal key directly
        min_key = None
        for i, (rx, ry) in enumerate(resources):
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (-(do - ds), ds, do, i)
            if min_key is None or key < min_key:
                min_key = key

        key = (min_key[0], min_key[1], min_key[2], min_key[3], dx, dy)
        if key < best_move:
            best_move = (key[0], dx, dy)

    if best_move[0] == 10**18:
        return [0, 0]
    return [best_move[1], best_move[2]]