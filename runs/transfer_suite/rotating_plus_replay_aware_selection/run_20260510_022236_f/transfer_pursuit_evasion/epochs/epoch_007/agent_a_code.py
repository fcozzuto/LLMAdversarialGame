def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("pursuer" in role)
    # In case role naming is different, default: act as pursuer.
    if ("evad" in role) and ("purs" not in role):
        pursuer = False

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    moves = [(dx, dy) for dx in dxs for dy in dys]
    t = int(observation.get("turn_index", 0))

    best_move = [0, 0]
    best = None

    dx = ox - sx
    dy = oy - sy
    stepx = 0 if dx == 0 else (1 if dx > 0 else -1)
    stepy = 0 if dy == 0 else (1 if dy > 0 else -1)

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not ok(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        same = (nx == ox and ny == oy)

        # Predict a bit against zigzag: prefer alternating perpendicular bias to reduce opponent's escape lines.
        # For pursuer: move generally toward opponent plus a parity-dependent slight perpendicular.
        # For evader: move generally away plus parity-dependent perpendicular.
        perp = (-stepy, stepx)
        bias_x, bias_y = perp if (t % 2 == 0) else (stepy, -stepx)
        align = (mdx * bias_x + mdy * bias_y)

        if pursuer:
            # avoid stepping onto opponent only if we are not sure? capture is good, so keep.
            val = (dist2, 0 if not same else -1, -align)
            # primary: minimize dist2
            key = val
            better = best is None or key < best
        else:
            # avoid being captured (evader should strongly avoid same cell)
            val = (-dist2, 1 if same else 0, align)
            # primary: maximize dist2 => minimize -dist2
            key = val
            better = best is None or key < best

        if better:
            best = key
            best_move = [mdx, mdy]

    return [int(best_move[0]), int(best_move[1])]