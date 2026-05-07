def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    resources_raw = observation.get("resources", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    for x, y in resources:
        my_d = man(sx, sy, x, y)
        op_d = man(ox, oy, x, y)
        # Prefer cells where we are closer than opponent; tie-break for fewer our steps.
        score = (op_d - my_d, -(my_d), x, y)
        if best is None or score > best[0]:
            best = (score, (x, y))
    tx, ty = best[1]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (-(10**9), None)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        my_d = man(nx, ny, tx, ty)
        op_d = man(ox, oy, tx, ty)
        # Greedy toward target, but if multiple, prefer improving our advantage.
        adv_now = op_d - my_d
        # Small preference for also moving generally toward target to avoid dithering.
        bias = -(abs(nx - tx) + abs(ny - ty))
        cand = (adv_now, bias)
        if best_move[1] is None or cand > best_move[0]:
            best_move = (cand, [dx, dy])

    return best_move[1] if best_move[1] is not None else [0, 0]