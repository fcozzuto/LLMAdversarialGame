def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx0 = (w - 1) / 2.0
    cy0 = (h - 1) / 2.0

    best_res = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        score = (od - sd) * 8 - sd
        center_bias = -(((rx - cx0) ** 2) + ((ry - cy0) ** 2)) * 1e-4
        t = score + center_bias
        if best_res is None or t > best_res[0]:
            best_res = (t, rx, ry)

    _, tx, ty = best_res

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_t = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        self_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        # Prefer moves that increase the "denial gap" (opponent farther than us), then minimize our distance.
        t = (opp_d - self_d) * 10 - self_d
        # Small tie-break to keep progress toward target
        t += -md(nx, ny, tx, ty) * 0.01
        if best_t is None or t > best_t:
            best_t = t
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]