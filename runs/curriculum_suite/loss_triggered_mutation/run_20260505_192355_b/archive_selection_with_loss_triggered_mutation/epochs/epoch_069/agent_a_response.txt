def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        my_pos = (nx, ny)
        best_val = None
        for rx, ry in resources:
            rpos = (rx, ry)
            md = d(my_pos, rpos)
            od = d((ox, oy), rpos)
            lead = od - md  # positive means I'm closer than opponent
            # Prefer taking lead; if tie, prefer closer and slightly prefer moving toward center
            center_bias = - (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.01
            key = (-(lead + center_bias), md, od, rx, ry)
            if best_val is None or key < best_val:
                best_val = key

        # Now choose move based on best resource evaluation; prefer higher lead overall
        lead_key = best_val[0]
        score_tuple = (lead_key, best_val[1], best_val[2], dx, dy)
        if best is None or score_tuple < best[0]:
            best = (score_tuple, dx, dy)

    return [best[1], best[2]] if best else [0, 0]