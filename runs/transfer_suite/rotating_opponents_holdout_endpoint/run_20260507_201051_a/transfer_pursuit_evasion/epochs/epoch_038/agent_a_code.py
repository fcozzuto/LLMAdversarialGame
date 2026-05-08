def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_list = observation.get("obstacles") or []
    obs = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def corner_score(x, y):
        # maximize for evader, minimize for pursuer via later sign
        return max(abs(x - cx) + abs(y - cy) for cx, cy in corners)

    best_dxdy = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        d = dist2(nx, ny)
        c = corner_score(nx, ny)

        # wall-run-ish: prefer staying adjacent to obstacles while progressing (evader) or hunting (pursuer)
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obs:
                    adj += 1

        if i_am_evader:
            key = (d, c, adj)
        else:
            # pursuer: reduce distance, reduce corner distance, increase adjacency to trap
            key = (-d, -c, adj)

        if best_key is None or key > best_key or (key == best_key and (dx, dy) < best_dxdy):
            best_key = key
            best_dxdy = (dx, dy)

    if best_dxdy is None:
        return [0, 0]
    return [int(best_dxdy[0]), int(best_dxdy[1])]