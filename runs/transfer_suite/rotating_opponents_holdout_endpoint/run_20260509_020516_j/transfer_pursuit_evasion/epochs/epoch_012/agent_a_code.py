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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    i_am_pursuer = "pursuer" in role and "evader" not in role

    my_best = None
    best_val = -10**18
    # If pursuer: maximize score = (close) => maximize -distance; opponent assumed adversarial by maximizing distance.
    # If evader: maximize score = (far) => maximize distance; opponent adversarial by minimizing distance.
    for mdx, mdy in deltas:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        worst = None
        for odx, ody in deltas:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                continue
            dist = d2(nx, ny, tx, ty)
            if i_am_pursuer:
                cand = -dist  # opponent will reduce our progress => choose smaller cand
                if worst is None or cand < worst:
                    worst = cand
            else:
                cand = dist   # opponent will get closer => choose smaller distance
                if worst is None or cand < worst:
                    worst = cand
        if worst is None:
            continue
        # Small tie-break: prefer moves that also keep away from obstacles locally.
        if i_am_pursuer:
            tie = -min(d2(nx + ax, ny + ay, ox + 0, oy + 0) for ax in (-1, 0, 1) for ay in (-1, 0, 1) if valid(nx + ax, ny + ay))
        else:
            tie = -min(d2(nx + ax, ny + ay, ox + 0, oy + 0) for ax in (-1, 0, 1) for ay in (-1, 0, 1) if valid(nx + ax, ny + ay))
        val = (worst * 10) + tie
        if my_best is None or val > best_val:
            my_best = (mdx, mdy)
            best_val = val

    if my_best is None:
        return [0, 0]
    return [int(my_best[0]), int(my_best[1])]