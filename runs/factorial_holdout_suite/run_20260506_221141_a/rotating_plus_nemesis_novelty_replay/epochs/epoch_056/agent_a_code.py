def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs_set.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs_set:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None  # (adv, -opp_d, self_d, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obs_set:
            continue

        local_best = None
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - self_d  # positive means we are closer to take it first
            key = (adv, -opp_d, self_d, rx, ry)
            if local_best is None or key > local_best:
                local_best = key

        if local_best is None:
            continue
        if best is None or local_best > best:
            best = local_best

    if best is None:
        return [0, 0]
    _, _, _, tx, ty = best

    target_x, target_y = tx, ty
    step_dx = 0
    if target_x > sx:
        step_dx = 1
    elif target_x < sx:
        step_dx = -1
    step_dy = 0
    if target_y > sy:
        step_dy = 1
    elif target_y < sy:
        step_dy = -1

    nx, ny = sx + step_dx, sy + step_dy
    if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs_set:
        return [step_dx, step_dy]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs_set:
            if cheb(nx, ny, target_x, target_y) < cheb(sx, sy, target_x, target_y):
                return [dx, dy]
    return [0, 0]