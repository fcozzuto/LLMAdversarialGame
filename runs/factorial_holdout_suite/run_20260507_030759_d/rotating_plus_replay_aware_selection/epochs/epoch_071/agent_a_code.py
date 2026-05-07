def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(a, b, c, e):
        return max(abs(c - a), abs(e - b))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if w <= 0 or h <= 0 or not resources:
        return [0, 0]

    # Pick a target resource with priority to those we can arrive to no later than the opponent.
    best_res = None
    best_val = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        st = d(sx, sy, rx, ry)
        ot = d(ox, oy, rx, ry)
        diff = ot - st  # positive => we are earlier
        # Tie-break friendly: if we tie, still prefer (slightly) earlier; otherwise contest closest-to-tie.
        val = diff * 2000 - st * 10 + (rx + ry) * 0.01
        if st == ot:
            val += 500
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]
    tx, ty = best_res

    # Choose move that improves our arrival advantage to target; secondary: reduce distance.
    best_move = (0, 0)
    best_mv_val = -10**18
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue
        st_next = d(nsx, nsy, tx, ty)
        ot_now = d(ox, oy, tx, ty)
        diff_next = ot_now - st_next
        mv_val = diff_next * 2000 - st_next * 10 - (0 if (mdx == 0 and mdy == 0) else 1) * 0.01
        # Small preference for moves that align toward target to avoid dithering
        align = (1 if tx == nsx else 0) + (1 if ty == nsy else 0) + (1 if (mx := (tx - nsx)) == 0 else 0)
        mv_val += align * 0.001
        if mv_val > best_mv_val:
            best_mv_val = mv_val
            best_move = (mdx, mdy)

    dx, dy = best_move
    return [int(dx), int(dy)]