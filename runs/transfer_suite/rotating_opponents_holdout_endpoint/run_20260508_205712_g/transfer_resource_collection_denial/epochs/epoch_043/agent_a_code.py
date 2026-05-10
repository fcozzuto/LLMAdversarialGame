def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    res_set = set((r[0], r[1]) for r in resources)
    obs_set = set((p[0], p[1]) for p in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_advantage_distance(nx, ny):
        if not resources:
            return None
        # maximize (opp_d - our_d); tie-break toward our closeness then deterministic coordinates
        best = None
        for rx, ry in sorted(res_set):
            our_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            adv = opp_d - our_d
            key = (adv, -our_d, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, our_d)
        return best[0]

    def cell_penalty(nx, ny):
        # Avoid obstacles; prefer cells not immediately adjacent to obstacles (soft)
        if (nx, ny) in obs_set:
            return 10**9
        pen = 0
        for ax, ay in obstacles:
            d = max(abs(nx - ax), abs(ny - ay))
            if d == 0:
                pen += 1000
            elif d == 1:
                pen += 2
        return pen

    if not resources:
        # No resources: move toward center while keeping distance from opponent
        cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            dcent = abs(nx - cx) + abs(ny - cy)
            dop = manh(nx, ny, ox, oy)
            key = (-dcent, dop, dx, dy)
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        return best[1] if best is not None else [0, 0]

    best_move = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        immediate = 1 if (nx, ny) in res_set else 0
        adv_key = best_advantage_distance(nx, ny)
        if adv_key is None:
            continue
        # Encourage staying slightly away from opponent while racing a chosen resource
        dop = manh(nx, ny, ox, oy)
        pen = cell_penalty(nx, ny)
        # Score key: maximize advantage, then immediate pickup, then keep distance from opponent, then deterministic move
        key = (adv_key[0], immediate, dop, -pen, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return list(best_move) if best_move is not None else [0, 0]