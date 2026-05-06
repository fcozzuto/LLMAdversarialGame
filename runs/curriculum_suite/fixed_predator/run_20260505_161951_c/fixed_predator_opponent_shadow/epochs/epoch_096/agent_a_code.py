def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            k = (md(nx, ny, tx, ty), md(nx, ny, ox, oy))
            if best is None or k < best[0]:
                best = (k, (dx, dy))
        return [best[1][0], best[1][1]]

    # Nearest resource targets for both agents
    my_dists = [(md(sx, sy, rx, ry), rx, ry) for rx, ry in resources]
    op_dists = [(md(ox, oy, rx, ry), rx, ry) for rx, ry in resources]
    my_best = min(my_dists)[0]
    op_best = min(op_dists)[0]
    my_target = min(my_dists)[1:]
    op_target = min(op_dists)[1:]

    # Resource "value" heuristic: prefer closer resources, but also deny opponent's closest
    denom = len(resources) if len(resources) else 1
    cx = sum(p[0] for p in resources) / denom
    cy = sum(p[1] for p in resources) / denom

    def move_value(dx, dy):
        nx, ny = sx + dx, sy + dy
        my_min = 10**9
        op_min = 10**9
        deny = 0
        gain = 0
        for rx, ry in resources:
            d_self = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            # If we can beat opponent on a resource sooner, it's valuable
            diff = d_opp - d_self
            if d_self < my_min:
                my_min = d_self
            if d_opp < op_min:
                op_min = d_opp
            # Weight by how near the resource is to both (avoid far-away traps)
            w = 1.0 / (1 + (md(rx, ry, cx, cy) if isinstance(cx, float) else md(rx, ry, cx, cy)))
            gain += max(0, diff) * w
            deny += max(0, -diff) * w
        # Also directly steer away from opponent target if it doesn't cost too much
        cost_to_my = md(nx, ny, my_target[0], my_target[1])
        cost_to_op = md(nx, ny, op_target[0], op_target[1])
        # Main objective: improve our closeness relative to opponent and maximize "gain"; penalize deny
        # Secondary: move that reduces opponent's effective access by stepping away from their closest target
        return (-(op_best - op_min) + (op_best - my_min) + 2.0 * gain - 1.5 * deny,
                md(nx, ny, my_target[0], my_target[1]) + 0.25 * md(nx, ny, op_target[0], op_target[1]),
                md(nx, ny, int(cx), int(cy)))

    best = None
    best_k = None
    for dx, dy in valid:
        k = move_value(dx, dy)
        if best_k is None or k > best_k:
            best_k = k
            best = (dx, dy)
        elif k == best_k and (dx, dy) < best:
            best = (dx, dy)
    return [best[0], best[1]]