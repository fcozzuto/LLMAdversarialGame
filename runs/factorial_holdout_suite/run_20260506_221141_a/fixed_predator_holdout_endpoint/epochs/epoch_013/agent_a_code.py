def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for a in obstacles:
        try:
            x, y = a
            obst.add((int(x), int(y)))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_score = -10**18

    any_res = False
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        score = 0
        min_self = 10**9
        min_opp = 10**9
        closest_res_dir = None

        for r in resources:
            try:
                rx, ry = r
            except Exception:
                continue
            rx, ry = int(rx), int(ry)
            any_res = True
            d1 = md(nx, ny, rx, ry)
            d2 = md(ox, oy, rx, ry)
            if d1 < min_self:
                min_self = d1
            if d2 < min_opp:
                min_opp = d2
            score += (d2 - d1)  # prefer positions where we beat opponent on resources
        if any_res:
            # also prefer reducing distance to closest resource we can contest
            score += 20 * (min_opp - min_self)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    if not any_res:
        # move deterministically away from opponent if no resources provided
        tx = -1 if ox > sx else (1 if ox < sx else 0)
        ty = -1 if oy > sy else (1 if oy < sy else 0)
        cand = [tx, ty]
        dx, dy = cand[0], cand[1]
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            return [int(dx), int(dy)]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]