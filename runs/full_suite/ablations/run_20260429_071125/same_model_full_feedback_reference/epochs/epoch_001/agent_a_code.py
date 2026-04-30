def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw, gh = observation.get("grid_width", 0), observation.get("grid_height", 0)
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list if p is not None and len(p) >= 2)
    resources = observation.get("resources", []) or []

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if gw <= 0 or gh <= 0:
        return [0, 0]

    if not resources:
        # Deterministic: move to maximize distance from opponent, avoiding obstacles
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
        best = None
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obstacles:
                continue
            key = (dist2(nx, ny, ox, oy), -abs(dx) - abs(dy), dx, dy)
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]] if best is not None else [0, 0]

    best_rx, best_ry = None, None
    best_adv = None
    for rx, ry in resources:
        ds = dist2(x, y, rx, ry)
        do = dist2(ox, oy, rx, ry)
        adv = do - ds
        if best_adv is None or adv > best_adv or (adv == best_adv and (rx, ry) < (best_rx, best_ry)):
            best_adv = adv
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obstacles:
            continue
        d_t = dist2(nx, ny, tx, ty)
        d_o = dist2(nx, ny, ox, oy)
        key = (-d_t, d_o, -abs(dx) - abs(dy), dx, dy)  # closer to target, farther from opponent
        if best is None or key > best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]] if best is not None else [0, 0]