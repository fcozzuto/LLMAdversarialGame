def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    d = max(abs(nx - tx), abs(ny - ty))
                    key = (d, abs(dx) + abs(dy), dx, dy)
                    if best is None or key < best[0]:
                        best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    def cheb(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    # Pick resource where we are relatively closer than opponent.
    best_res = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources with smaller ds; discourage those where opponent is much closer.
        score = (ds - 0.35 * do, ds, rx, ry)
        if best_res is None or score < best_res[0]:
            best_res = (score, (rx, ry))
    tx, ty = best_res[1]

    # Move greedily toward target while avoiding obstacles/out-of-bounds.
    best_move = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            # If tied, prefer reducing opponent advantage and staying stable.
            opp_d = cheb(nx, ny, ox, oy)
            key = (d, opp_d, abs(dx) + abs(dy), dx, dy)
            if best_move is None or key < best_move[0]:
                best_move = (key, [dx, dy])
    return best_move[1] if best_move else [0, 0]