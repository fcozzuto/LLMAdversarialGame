def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))

    def to_set(obj):
        s = set()
        for c in obj or []:
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                s.add((int(c[0]), int(c[1])))
        return s

    un = to_set(observation.get("unclaimed_cells"))
    myt = to_set(observation.get("self_territory"))
    opt = to_set(observation.get("opponent_territory"))
    obst = to_set(observation.get("obstacles"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_target_cell():
        adj_opt = []
        for (x, y) in un:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + dx, y + dy) in opt:
                    adj_opt.append((x, y))
                    break
        if adj_opt:
            return min(adj_opt, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        if un:
            # Prefer cells that would allow approach to opponent territory
            cells = list(un)
            return min(cells, key=lambda t: abs(t[0] - ox) + abs(t[1] - oy))
        # Fallback: move toward opponent territory boundary or position
        if opt:
            # pick closest opponent cell not blocked (deterministic)
            return min(list(opt), key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        return (sx, sy)

    tx, ty = best_target_cell()

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        # Value components: capture/flip potential, avoid giving opponent proximity, avoid being stuck.
        is_un = (nx, ny) in un
        is_opt = (nx, ny) in opt
        is_my = (nx, ny) in myt

        dist_to_target = abs(nx - tx) + abs(ny - ty)
        dist_to_opp = abs(nx - ox) + abs(ny - oy)

        adj_to_opt = 0
        for adx, ady in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (nx + adx, ny + ady) in opt:
                adj_to_opt += 1

        score = 0
        if is_un:
            score += 6
        if is_opt:
            score += 20  # flipping on entry
        if is_my:
            score += 1
        score += 3 * adj_to_opt
        score += -2.0 * dist_to_target
        score += 0.5 * (dist_to_opp)  # slightly keep distance from sweeper

        # small deterministic tie-break: prefer diagonal progress toward target, then x, then y
        prog = (1 if dx != 0 else 0) + (1 if dy != 0 else 0)
        score += 0.01 * prog
        if (score > best_score) or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]