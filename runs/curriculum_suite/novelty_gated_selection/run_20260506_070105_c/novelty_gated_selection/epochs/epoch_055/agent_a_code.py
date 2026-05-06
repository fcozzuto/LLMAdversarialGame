def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or []) if (int(r[0]), int(r[1])) not in obstacles]
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0)

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose target: primarily resources I'm closer to; secondary: avoid those opponent can reach much sooner.
    alpha = 1.0 + (t % 7) * 0.04  # deterministic small variation to avoid stuck niches
    beta = 0.25 if (t % 2 == 0) else 0.35
    best = None
    best_sc = None
    for rx, ry in resources:
        my_d = md((sx, sy), (rx, ry))
        opp_d = md((ox, oy), (rx, ry))
        # Lower is better for my_d/opp_d, so invert by maximizing negative "advantage" loss.
        sc = (opp_d - my_d * alpha) + beta * (my_d - opp_d)
        # Extra tie-break: prefer nearer overall early/mid-game.
        sc -= 0.01 * my_d * (1 if t < 20 else 0.7)
        if best_sc is None or sc > best_sc:
            best_sc, best = sc, (rx, ry)
    tx, ty = best

    # Evaluate next move by resulting positions.
    cur_d = md((sx, sy), (tx, ty))
    cur_opp = md((ox, oy), (tx, ty))
    best_mv = [0, 0]
    best_mv_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = md((nx, ny), (tx, ty))
        nod = md((ox, oy), (tx, ty))
        # Want to decrease distance to target and keep opponent from being closer than me.
        # Also prefer staying on a promising diagonal/line to reduce dithering.
        align = -abs((tx - nx) - (ty - ny))
        sc = (cur_d - nd) * 2.0 + (nod - cur_opp) * 0.1
        sc += (md((nx, ny), (ox, oy)) - md((sx, sy), (ox, oy))) * 0.05
        sc += align * 0.01
        # If I'm not closer than opponent after move, strongly discourage.
        if nd >= nod:
            sc -= 1.5 + 0.15 * (nd - nod)
        if best_mv_sc is None or sc > best_mv_sc:
            best_mv_sc = sc
            best_mv = [dx, dy]

    return best_mv