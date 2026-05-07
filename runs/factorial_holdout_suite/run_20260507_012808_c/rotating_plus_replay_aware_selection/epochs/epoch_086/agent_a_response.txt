def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp_to_valid(x, y):
        if valid(x, y):
            return x, y
        return None

    # If no resources, drift to center to reduce future distance
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        best_key = (-10**9, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            key = (-d, d)
            if key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = [0, 0]
    best_key = (-10**18, -10**18, -10**18)

    res_list = [tuple(r) for r in resources]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Immediate collect if stepping onto a resource
        if (nx, ny) in obstacles:
            continue

        # Evaluate: after moving, how good is our best attainable resource race?
        best_margin = -10**18
        best_selfd = 10**18
        best_oppd = 10**18
        for rx, ry in res_list:
            if rx == nx and ry == ny:
                # Hard prioritize stepping onto a resource cell
                md = 10**9
                margin = md
                selfd = 0
                oppd = cheb(ox, oy, rx, ry)
            else:
                selfd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                margin = oppd - selfd  # larger means we get there first (or at least closer)
            if (margin > best_margin) or (margin == best_margin and selfd < best_selfd) or (margin == best_margin and selfd == best_selfd and oppd < best_oppd):
                best_margin, best_selfd, best_oppd = margin, selfd, oppd

        # Additional shaping: keep moving toward the currently closest resource to avoid stalls
        closest_now = 10**18
        for rx, ry in res_list:
            d0 = cheb(nx, ny, rx, ry)
            if d0 < closest_now:
                closest_now = d0

        # Key: maximize race margin, then minimize time to some resource, then minimize absolute opponent distance
        key = (best_margin, -best_selfd, -best_oppd)
        # Secondary: prefer smaller closest distance if still tied
        key2 = (key[0], key[1], key[2], -closest_now)
        if key2 > (best_key[0], best_key[1], best_key[2], -10**18):
            best_key = (key[0], key[1], key[2])
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]