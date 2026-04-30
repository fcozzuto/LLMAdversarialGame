def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid_res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                valid_res.append((x, y))

    if not valid_res:
        # No resources: move toward opponent's quadrant opposite from us (stabilize)
        tx = 0 if sx > w // 2 else w - 1
        ty = 0 if sy > h // 2 else h - 1
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = cheb(nx, ny, tx, ty)
            if -d > best[2]:
                best = (dx, dy, -d)
        return [best[0], best[1]]

    # Pick a target resource where we are relatively closer than opponent.
    # Also bias toward resources that are "ahead" of our motion direction (toward enemy corner).
    toward_x = 1 if ox < sx else -1 if ox > sx else 0
    toward_y = 1 if oy < sy else -1 if oy > sy else 0

    best_t = None
    best_score = -10**18
    for rx, ry in valid_res:
        du = cheb(sx, sy, rx, ry)
        dv = cheb(ox, oy, rx, ry)
        if du == 0:
            return [0, 0]
        # Use a closeness advantage score; prefer resources we can reach sooner.
        # Add slight directional preference to get materially different from last epoch.
        dir_pref = (rx - sx) * toward_x + (ry - sy) * toward_y
        # remaining_resource_count creates late-game bias to secure nearer resources.
        rem = int(observation.get("remaining_resource_count", len(valid_res)) or len(valid_res))
        late = 1.0 if rem <= 6 else 0.0
        score = (dv - du) * 8.0 + dir_pref * 0.2 + (-(du)) * (1.5 + 2.0 * late)
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t

    rem = int(observation.get("remaining_resource_count", len(valid_res)) or len(valid_res))
    late = 1.0 if rem <= 6 else 0.0

    # Choose move that best advances toward target while reducing opponent access.
    best_m = (0, 0, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (