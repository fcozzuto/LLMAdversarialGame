def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    respos = []
    for r in resources:
        try:
            x, y = r
            respos.append((x, y))
        except:
            pass

    if not respos:
        # No resources visible: move toward center-ish avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                sc = -(abs(nx - cx) + abs(ny - cy))
                if sc > best[0]:
                    best = (sc, dx, dy)
        return [best[1], best[2]]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_sc, best_dx, best_dy = -10**18, 0, 0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose a target as the closest resource from our new position
        my_best_d = 10**9
        my_best_r = None
        for rx, ry in respos:
            d = abs(nx - rx) + abs(ny - ry)
            if d < my_best_d:
                my_best_d = d
                my_best_r = (rx, ry)

        rx, ry = my_best_r
        sc = -my_best_d

        # Anti-acceleration: discourage moves that make opponent significantly closer to the same target
        if opp_exists:
            opp_d_now = abs(ox - rx) + abs(oy - ry)
            opp_d_after = abs(ox - rx) + abs(oy - ry)
            # We don't know opponent's move, so use relative threat based on our progress and distance gap
            my_d_now = abs(sx - rx) + abs(sy - ry)
            gap_now = opp_d_now - my_d_now
            gap_after = opp_d_now - my_best_d
            # If our move worsens the gap (opponent becomes relatively closer), penalize
            sc += 0.6 * (gap_after - gap_now)

        # Slight obstacle/edge hugging penalty via preference to closer-than-current resource
        if my_best_d > abs(sx - rx) + abs(sy - ry):
            sc -= 0.15

        if sc > best_sc:
            best_sc, best_dx, best_dy = sc, dx, dy

    return [int(best_dx), int(best_dy)]