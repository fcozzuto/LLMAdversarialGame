def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    op_adj = None
    if opT:
        # choose a deterministic adjacent-opponent target if we can reach it in 1 step
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in opT:
                op_adj = (nx, ny)
                break

    un_target = None
    if unT:
        un_list = list(unT)
        un_list.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - cx) + abs(p[1] - cy), p[0], p[1]))
        un_target = un_list[0]

    best = (-(10**9), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0

        cell = (nx, ny)
        score = 0.0
        if cell in opT:
            score += 6.0
            # prefer flipping cells closer to center to deny edge growth
            score += -(abs(nx - cx) + abs(ny - cy)) * 0.02
        elif cell in unT:
            score += 3.0
            score += -(abs(nx - cx) + abs(ny - cy)) * 0.03
            if un_target is not None:
                score += -(abs(nx - un_target[0]) + abs(ny - un_target[1])) * 0.01
        elif cell in selfT:
            score += 0.8
            score += -(abs(nx - cx) + abs(ny - cy)) * 0.01

        # keep moving toward where unclaimed/opponent density is (deterministic via nearest)
        if opT:
            # approximate nearest opponent with a fixed sample: corners + any adjacent-op
            if op_adj is not None and cell == op_adj:
                score += 0.5
            else:
                corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
                score += -min(abs(nx - px) + abs(ny - py) for px, py in corners) * 0.001
        if un_target is not None:
            score += -((abs(nx - un_target[0]) + abs(ny - un_target[1])) * 0.01)

        # tie-break deterministically by move order
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]