def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    px, py = int(op[0]), int(op[1])

    obs = set()
    for c in observation.get("obstacles", []) or []:
        if c is not None and len(c) >= 2:
            try:
                obs.add((int(c[0]), int(c[1])))
            except:
                pass

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    unclaimed = observation.get("unclaimed_cells") or []
    obstacles_near = lambda x, y: sum(1 for dx, dy in dirs if inb(x + dx, y + dy) and (x + dx, y + dy) in obs)

    def man(a, b, c, d):  # manhattan
        return abs(a - c) + abs(b - d)

    if unclaimed:
        # Deterministic target: closest to our corner-biased direction (prefer top-left if we're near it, else opposite)
        corner_bias_x = 0 if sx <= (w - 1) // 2 else (w - 1)
        corner_bias_y = 0 if sy <= (h - 1) // 2 else (h - 1)
        target = min(unclaimed, key=lambda t: (man(t[0], t[1], corner_bias_x, corner_bias_y), t[1], t[0]))
        tx, ty = int(target[0]), int(target[1])
        target_present = True
    else:
        # No unclaimed: go to the farthest corner from opponent
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (abs(c[0] - px) + abs(c[1] - py), c[1], c[0]))
        target_present = False

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist2_opp = (nx - px) * (nx - px) + (ny - py) * (ny - py)
        dist_to_target = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        # If unclaimed exists, also favor moving toward the nearest unclaimed from the candidate (one-step lookahead).
        if target_present:
            near = 10**9
            for uc in unclaimed[:min(12, len(unclaimed))]:
                ux, uy = int(uc[0]), int(uc[1])
                near = min(near, (nx - ux) * (nx - ux) + (ny - uy) * (ny - uy))
            near_term = near
        else:
            near_term = dist_to_target
        val = dist2_opp * 1.0 - 0.35 * near_term - 1.2 * obstacles_near(nx, ny)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move