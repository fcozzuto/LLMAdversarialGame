def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Pick a resource where we are ahead in the race; then prefer smaller my distance.
    best_r = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        key = (opp_d - my_d, -my_d, -(rx + ry), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    # Choose next step that advances race, avoids obstacles, and improves distance to target.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            my_next = cheb(nx, ny, tx, ty)
            opp_now = cheb(ox, oy, tx, ty)
            # Higher is better: we want (opp_distance - my_distance) to increase, and my distance to decrease.
            race = (opp_now - my_next)
            candidates.append(((race, -my_next, -(dx * dx + dy * dy), dx, dy), nx, ny))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0], reverse=True)
    _, nx, ny = candidates[0]
    return [int(nx - sx), int(ny - sy)]