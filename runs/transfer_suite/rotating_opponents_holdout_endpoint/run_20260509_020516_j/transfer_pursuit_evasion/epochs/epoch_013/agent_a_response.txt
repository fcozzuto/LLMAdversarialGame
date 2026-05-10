def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    i_am_pursuer = "pursuer" in role and "evader" not in role

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if i_am_pursuer:
        # Evader likely aims for the corner farthest from us.
        tx, ty = max(corners, key=lambda c: (sx - c[0]) * (sx - c[0]) + (sy - c[1]) * (sy - c[1]))
    else:
        # We aim for the corner farthest from pursuer (opponent).
        tx, ty = max(corners, key=lambda c: (ox - c[0]) * (ox - c[0]) + (oy - c[1]) * (oy - c[1]))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best_move = (0, 0)
    if i_am_pursuer:
        best_score = -10**18
        for mdx, mdy in deltas:
            nx, ny = sx + mdx, sy + mdy
            if not valid(nx, ny):
                continue
            dist_opp = d2(nx, ny, ox, oy)
            dist_opp_to_target = d2(ox, oy, tx, ty)
            # Reduce our distance; also try to keep evader away from their target.
            score = -dist_opp + 0.25 * dist_opp_to_target
            if score > best_score:
                best_score = score
                best_move = (mdx, mdy)
    else:
        best_score = -10**18
        for mdx, mdy in deltas:
            nx, ny = sx + mdx, sy + mdy
            if not valid(nx, ny):
                continue
            dist_to_pursuer = d2(nx, ny, ox, oy)
            dist_to_target = d2(nx, ny, tx, ty)
            # Stay far and head to target corner.
            score = dist_to_pursuer - 0.1 * dist_to_target
            if score > best_score:
                best_score = score
                best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]