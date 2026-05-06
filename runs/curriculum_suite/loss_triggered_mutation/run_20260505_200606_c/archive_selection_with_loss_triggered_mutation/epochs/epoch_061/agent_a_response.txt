def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    have_res = bool(res)
    if have_res:
        tx, ty = min(res, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        tx, ty = (sx - (ox - sx)), (sy - (oy - sy))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    # Heuristic weights: seek resources, keep away from opponent, avoid getting closer unless it helps resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dres = man(nx, ny, tx, ty)
        dopp = man(nx, ny, ox, oy)
        dres_cur = man(sx, sy, tx, ty)
        dopp_cur = man(sx, sy, ox, oy)

        if have_res:
            # Lower is better: reduce resource distance; penalty if moving toward opponent too much.
            delta_res = dres - dres_cur
            delta_opp = dopp_cur - dopp
            # Encourage immediate resource capture by hardening resource distance.
            score = (dres * 1000) + (delta_res * 30) + (delta_opp * 12)
        else:
            # No resources: maximize opponent distance while still moving deterministically away from it.
            score = ((-dopp) * 1000) + ((man(nx, ny, tx, ty)) * 2)

        # Deterministic tie-break: prefer moves that change position less "randomly" (dx,dy order) but still deterministic.
        key = (score, 0 if (dx == 0 and dy == 0) else -1, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]