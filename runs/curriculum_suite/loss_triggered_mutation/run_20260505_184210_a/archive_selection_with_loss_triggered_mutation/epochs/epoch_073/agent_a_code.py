def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def ok_next(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [int(dx), int(dy)]

    best_move = (0, 0)
    best_val = -10**18

    me = (sx, sy)
    opp = (ox, oy)

    # Step-evaluation with resource "race" pressure and obstacle proximity penalty
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok_next(nx, ny):
            nx, ny = sx, sy
        nme = (nx, ny)

        # obstacle proximity: avoid stepping adjacent to obstacles
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    prox -= 2

        # race heuristic: prefer resources I'm closer to; if none, minimize worst-case race time
        score = prox
        local_best = 10**9
        local_win = -10**9
        for r in resources:
            dm = man(nme, r)
            do = man(opp, r)
            # win-more term: higher when I'm closer by margin
            local_win = max(local_win, (do - dm) * 3 - dm)
            # worst-case time to reach
            t = dm if dm > do else (do)
            if t < local_best:
                local_best = t
        score += local_win
        score += -local_best

        # minor tie-break: prefer progressing toward center to reduce oscillations
        cx, cy = w // 2, h // 2
        score += -man(nme, (cx, cy)) * 0.05

        if score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]