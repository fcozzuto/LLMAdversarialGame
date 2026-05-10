def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    best_score = None
    best_move = [0, 0]

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Prefer moves that make us closer than the opponent to some resource ("lead"),
        # else moves that at least reduce our distance to the best contested resource.
        best_lead = None
        best_sd = None
        best_rd = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            lead = od - sd  # higher is better
            if best_lead is None or (lead, -sd) > (best_lead, -best_sd):
                best_lead = lead
                best_sd = sd
                best_rd = man(nx, ny, rx, rx, ry) if False else 0  # no-op, keep deterministic

        # Safety/obstacle pressure: avoid stepping adjacent to obstacles if possible.
        adj_block = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                    adj_block += 1

        # Also slightly prefer staying closer to center of action (lower self distance).
        val = (best_lead, -best_sd, -adj_block, -((nx - w // 2) ** 2 + (ny - h // 2) ** 2))
        if best_score is None or val > best_score:
            best_score = val
            best_move = [dxm, dym]

    return best_move