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

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_step(target):
        tx, ty = target
        cand = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((man((nx, ny), target), dx, dy))
        if not cand:
            return (0, 0)
        cand.sort(key=lambda t: (t[0], t[1], t[2]))
        return (cand[0][1], cand[0][2])

    if not resources:
        tx, ty = w // 2, h // 2
        return list(best_step((tx, ty)))

    me = (sx, sy)
    opp = (ox, oy)
    choices = []
    for r in resources:
        d1 = man(me, r)
        d2 = man(opp, r)
        # Prefer resources we can reach no later than opponent; then minimize our distance.
        if d1 <= d2:
            choices.append((0, d1 - d2, d1, r))
        else:
            # If we can't secure any, contest the resource where opponent is most ahead but closest to us.
            choices.append((1, d2 - d1, d1, r))

    # Sort: first secure if possible; otherwise minimize opponent advantage, then our distance.
    choices.sort(key=lambda t: (t[0], t[1], t[2], t[3][0], t[3][1]))
    target = choices[0][3]
    dx, dy = best_step(target)
    return [int(dx), int(dy)]