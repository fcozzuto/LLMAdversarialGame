def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_t = None
    best_key = None
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        key = (od - sd, -sd, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            nsd = cheb(nx, ny, tx, ty)
            nod = cheb(ox, oy, tx, ty)
            adv = nod - nsd
            odist_next = cheb(ox, oy, nx, ny)
            # Prefer improving our advantage to the target; then reduce distance to it;
            # if still tied, move to increase distance from opponent to reduce contest.
            key = (adv, -nsd, odist_next, dx, dy)
            candidates.append((key, [dx, dy]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]