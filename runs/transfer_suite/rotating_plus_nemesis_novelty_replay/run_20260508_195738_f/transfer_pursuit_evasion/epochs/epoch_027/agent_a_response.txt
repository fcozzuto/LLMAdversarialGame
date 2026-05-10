def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    roles = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    self_is_evader = ("evader" in roles) and ("purs" not in roles)

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((int(p[0]), int(p[1])))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    dxdy_list = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    target_corner = corners[0]
    best_cd = -1
    for cx, cy in corners:
        cd = abs(cx - ox) + abs(cy - oy)
        if cd > best_cd:
            best_cd = cd
            target_corner = (cx, cy)
    tcx, tcy = target_corner

    best_move = (0, 0)
    if self_is_evader:
        best_key = None
        for dx, dy in dxdy_list:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            d = dist2(nx, ny, ox, oy)
            corner_push = abs(tcx - nx) + abs(tcy - ny)
            # small preference for reducing "escape-blocking" near obstacles
            near_obs = 0
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    ax, ay = nx + adx, ny + ady
                    if (ax, ay) in obs_set:
                        near_obs += 1
            key = (d, corner_push, -near_obs, -abs(dx) - abs(dy), -nx, -ny)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        best_key = None
        for dx, dy in dxdy_list:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            d = dist2(nx, ny, ox, oy)
            # encourage pushing toward farthest corner from evader (acts as predictable net)
            corner_pull = abs(ox - tcx) + abs(oy - tcy)
            # prefer moves that reduce distance more even if corner_pull same
            key = (-d, corner_pull, -(abs(dx) + abs(dy)), nx, ny)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]