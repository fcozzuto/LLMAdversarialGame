def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((x, y) for x, y in obstacles)

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(a, b): 
        dx = a[0] - b[0]; dy = a[1] - b[1]
        return dx*dx + dy*dy

    if resources:
        best_t = None
        best_key = None
        for tx, ty in resources:
            if (tx, ty) in obs_set: 
                continue
            sd = dist2((sx, sy), (tx, ty))
            od = dist2((ox, oy), (tx, ty))
            diff = od - sd
            key = (diff, -sd)  # maximize diff, then minimize sd
            if best_key is None or key > best_key:
                best_key = key
                best_t = (tx, ty)
        tx, ty = best_t if best_t is not None else (sx, sy)
        # choose move that gets closer to target while avoiding obstacles
        best_move = (0, 0)
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            nd = dist2((nx, ny), (tx, ty))
            # mild tie-breaker: avoid giving opponent too good a route
            opp_nd = dist2((ox, oy), (tx, ty))
            val = (-nd, (opp_nd - nd))  # smaller nd better; second prefers where we stay advantage
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: go to center-biased toward opponent
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    tx = int(round(cx))
    ty = int(round(cy))
    if abs(ox - sx) + abs(oy - sy) > 0:
        # also drift toward opponent to create contention
        if abs(ox - sx) >= abs(oy - sy):
            ty = int(round(cy + (oy - sy) * 0.25))
        else:
            tx = int(round(cx + (ox - sx) * 0.25))

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        # prefer closer to (tx,ty), avoid moving away from opponent too much
        val = (-dist2((nx, ny), (tx, ty)), -dist2((nx, ny), (ox, oy)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]