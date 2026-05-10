def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obstacle_set = set((x, y) for x, y in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacle_set
    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    rem = observation.get("remaining_resource_count", len(resources))
    # Prefer "we can reach before opponent" when resources are scarce; otherwise prioritize fastest grab for us.
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive => we are closer
        if rem <= 4:
            key = (-(margin), ds, rx, ry) if margin <= 0 else (0, -margin, ds, rx, ry)
        else:
            key = (-margin, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Evaluate candidate moves by distance to target and by denying opponent on that same target.
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # Also break ties by steering away from opponent slightly.
        opp_dist_self = cheb(nx, ny, ox, oy)
        cand.append(((ds2, -(do2 - ds2), -opp_dist_self, dx, dy), [dx, dy]))
    cand.sort()
    return cand[0][1] if cand else [0, 0]