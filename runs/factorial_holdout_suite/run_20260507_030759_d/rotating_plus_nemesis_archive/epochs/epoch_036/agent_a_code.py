def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))
        except Exception:
            pass

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
        except Exception:
            pass

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue

        if res:
            my_d = 10**9
            opp_d = 10**9
            for rx, ry in res:
                my_d = min(my_d, man(nx, ny, rx, ry))
                opp_d = min(opp_d, man(ox, oy, rx, ry))
            # Prefer being closer to remaining resources than opponent, with strong pull to nearest.
            score = (opp_d - my_d) * 500 - my_d * 5
            # If we're moving onto a resource, strongly prefer.
            if (nx, ny) in set(res):
                score += 10**6
            # Mildly bias to reduce distance to opponent only when we're not far from a resource.
            score += (op_d := man(nx, ny, ox, oy)) * (-1 if my_d <= 2 else -0.1)
        else:
            score = -man(nx, ny, ox, oy)

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]