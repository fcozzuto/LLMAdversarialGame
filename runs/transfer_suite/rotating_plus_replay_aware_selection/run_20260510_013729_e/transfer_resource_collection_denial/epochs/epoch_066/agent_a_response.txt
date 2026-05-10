def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    def cheb(a, b, c, d):
        dx = c - a
        if dx < 0:
            dx = -dx
        dy = d - b
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_val = -10**30
    best_move = [0, 0]

    for rx, ry in sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1])):
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        margin = opp_d - self_d

        # Pick a target with best capture advantage; if none, pick nearest to us.
        if margin > 0:
            target_val = (10**6) + margin * 1000 - self_d
        else:
            target_val = margin * 10 - self_d * 2 - opp_d

        if target_val > best_val:
            best_val = target_val
            target = (rx, ry)

    tx, ty = target
    best_step = -10**30
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        nds = cheb(nx, ny, tx, ty)
        ndo = cheb(ox, oy, tx, ty)
        # If we can match/beat opponent capture, prioritize getting there; else reduce our distance.
        step_margin = ndo - nds
        step_val = 2000 * (1 if step_margin > 0 else 0) + step_margin * 50 - nds
        # Small tie-break to keep behavior stable: prefer moves that approach target in x then y.
        step_val += -abs(nx - tx) * 0.01 - abs(ny - ty) * 0.001
        if step_val > best_step:
            best_step = step_val
            best_move = [dx, dy]

    return best_move