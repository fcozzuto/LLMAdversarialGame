def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        # deterministic fallback: try axis first, then stay
        if dx != 0:
            nx, ny = sx + dx, sy
            if 0 <= nx < w and (nx, sy) not in obstacles:
                return [dx, 0]
        if dy != 0:
            nx, ny = sx, sy + dy
            if 0 <= ny < h and (sx, ny) not in obstacles:
                return [0, dy]
        return [0, 0]

    # Predict opponent target as nearest resource to opponent.
    opp_target = min(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]), r[0], r[1]))
    ds_opp = cheb(sx, sy, opp_target[0], opp_target[1])
    do_opp = cheb(ox, oy, opp_target[0], opp_target[1])

    # If we can realistically get it first, contest it; otherwise, deny by choosing a far resource from opponent.
    if ds_opp <= do_opp:
        target = opp_target
    else:
        target = min(resources, key=lambda r: (-cheb(ox, oy, r[0], r[1]) , cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    return step_towards(target[0], target[1])