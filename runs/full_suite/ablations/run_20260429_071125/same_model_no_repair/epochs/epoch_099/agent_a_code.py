def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            t = (int(p[0]), int(p[1]))
            if t not in obstacles:
                resources.append(t)
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    # Pick a small deterministic set of promising targets based on opponent advantage.
    scored = []
    for i, (rx, ry) in enumerate(resources):
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        gain = opd - myd
        scored.append((gain, myd, i, rx, ry))
    scored.sort(key=lambda z: (-z[0], z[1], z[2]))
    targets = [(z[3], z[4]) for z in scored[:3]]

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        # Engine rejects invalid moves by keeping in place; treat out-of-bounds as staying.
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy
        if (nx, ny) in obstacles:
            val = -10**8  # strong penalty for hitting an obstacle
        else:
            val = -1
            # Choose target implicitly: maximize opponent-my-distance advantage from next step.
            for (rx, ry) in targets:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                advantage = opd - myd
                # Prefer moves that also slightly reduce my distance to the target.
                score = advantage * 100 - myd
                if score > val:
                    val = score
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: prefer smaller dx, then smaller dy, then (0,0).
            if best_move != (dx, dy):
                if (abs(dx), abs(dy), dx == 0 and dy == 0) < (abs(best_move[0]), abs(best_move[1]), best_move[0] == 0 and best_move[1] == 0):
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]