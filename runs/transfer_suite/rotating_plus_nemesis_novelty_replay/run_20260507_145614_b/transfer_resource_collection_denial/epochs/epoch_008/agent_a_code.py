def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_resource_for_move(nx, ny):
        if not resources:
            return None
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            if ds == 0:
                key = (10**12, -rx, -ry, 0)
                if best_key is None or key > best_key:
                    best_key = key
                    best = (rx, ry)
                continue
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent; also prefer closer ones.
            # Add a small bias toward center to reduce dithering.
            center_bias = -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2)
            key = (1000 + (do - ds) * 5 - ds + center_bias * 0.01, -ds, -do, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        best_d = 10**9
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best_d:
                best_d = d
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose move that maximizes immediate capture and improves distance advantage to a good target.
    res_set = set(tuple(r) for r in resources)
    best_score = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        captured = 1 if (nx, ny) in res_set else 0
        target = best_resource_for_move(nx, ny)
        if target is None:
            target = ((w - 1) // 2, (h - 1) // 2)

        rx, ry = target
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)

        # Score: capture heavily; otherwise aim for resources where we're closer than opponent.
        score = captured * 10**10 + (do - ds) * 200 - ds * 3

        # Tie-break deterministically: prefer staying toward opponent-advantage direction, then lexicographic move.
        tie = (-captured, (do - ds), -ds, -dx, -dy)
        if best_score is None or score > best_score or (score == best_score and tie > best_tie):
            best_score = score
            best_tie = tie
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]