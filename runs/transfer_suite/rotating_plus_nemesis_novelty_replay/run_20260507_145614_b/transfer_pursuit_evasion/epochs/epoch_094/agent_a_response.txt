def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("tag" in role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            penalty = 10**9
        else:
            penalty = 0
            for bx, by in obst:
                ddx, ddy = nx - bx, ny - by
                d = ddx * ddx + ddy * ddy
                if d == 0:
                    penalty = 10**9
                    break
                if d <= 4:
                    penalty += 500.0 / (1.0 + d)
        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy
        # pursuer: minimize distance; evader: maximize distance
        score = (-d2 if is_pursuer else d2) - penalty
        # tie-break deterministically: prefer staying near "better" side of the board
        if not is_pursuer:
            score += (nx + ny) * 0.01 - ((nx - (w - 1) / 2) ** 2 + (ny - (h - 1) / 2) ** 2) * 1e-6
        else:
            score += (nx * 0.0 + ny * 0.0)
        cand.append((score, dx, dy))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]