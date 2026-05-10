def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Heuristic: go for resource where we arrive earlier; also prefer resources "in front" (toward opponent corner)
    front = 1 if ox < sx else -1  # if opponent is left, "front" is -x; else +x
    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            nx, ny = sx, sy
        my_steps = cheb(nx, ny, ox, oy)
        # If we are too close, prioritize escaping slightly by minimizing closeness while still collecting
        escape = -1.5 * my_steps

        val = 0.0
        # contest-aware scoring over all resources (pick best destination)
        best_dest = -10**18
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Arrive earlier is primary; tie favors us by small offset
            win_term = (opd - myd)
            # Prefer resources that are more "forward" relative to opponent corner direction
            fwd = front * (rx - sx)
            # Slightly prefer keeping y aligned to reduce detours
            y_pen = abs(ny - ry) * 0.03
            score = 4.0 * win_term + 0.12 * fwd - 0.25 * myd - y_pen
            if score > best_dest:
                best_dest = score
        # Add escape only when very close to opponent; otherwise small weight
        val = best_dest + (escape if my_steps <= 2 else -0.05 * my_steps)

        # Deterministic tie-break: prefer moves with smaller absolute dx then dy, then lexicographic
        if val > best_val + 1e-9:
            best_val = val
            best_move = (dxm, dym)
        elif abs(val - best_val) <= 1e-9:
            cand = (abs(dxm), abs(dym), dxm, dym)
            bestc = (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1])
            if cand < bestc:
                best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]