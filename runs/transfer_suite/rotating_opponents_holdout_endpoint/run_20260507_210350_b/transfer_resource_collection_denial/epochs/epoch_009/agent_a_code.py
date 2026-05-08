def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid_step(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return False
        return (nx, ny) not in obstacles

    def pick_target(preferred=None, avoid=None):
        best_key = None
        best_r = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            if avoid is not None and (rx, ry) == avoid:
                continue
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # primary: beat opponent (ds < do); secondary: closeness advantage; tertiary: earlier pickup
            # Use discrete race slack to prioritize strong leads.
            lead = do - ds  # positive if we are closer
            can_race = 0 if ds <= do else 1  # 0 better (can beat), 1 worse
            key = (can_race, -lead, ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        if best_r is None:
            return preferred if preferred is not None else (w // 2, h // 2)
        return best_r

    if not resources:
        return [0, 0]

    # Choose initial target
    tx, ty = pick_target()
    # If opponent is extremely close to our target, switch to a different resource they are less likely to contest
    if cheb(ox, oy, tx, ty) <= 1 and len(resources) >= 2:
        tx, ty = pick_target(preferred=(tx, ty), avoid=(tx, ty))

    # Move one step toward target using Chebyshev-optimal delta; tie-break deterministically by direction order.
    dx = 0 if tx == x else (1 if tx > x else -1)
    dy = 0 if ty == y else (1 if ty > y else -1)

    # Try the intended diagonal first, then orthogonal, then stay; deterministic order.
    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for ddx, ddy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = x + ddx, y + ddy
        if valid_step(nx, ny) and (nx, ny) == (x + candidates[0][0], y + candidates[0][1]):
            return [ddx, ddy]
    for ddx, ddy in candidates:
        nx, ny = x + ddx, y + ddy
        if valid_step(nx, ny):
            return [ddx, ddy]

    return [0, 0]