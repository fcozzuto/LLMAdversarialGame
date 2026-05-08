def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def eval_cell(nx, ny):
        best_adv = -10**9
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            if od == 0 and sd > 0:
                adv = -10**6
            else:
                adv = (od - sd) * 1000 - sd  # prefer resources where opponent is farther
            if sd == 0:
                adv += 200000  # immediate collection
            if adv > best_adv:
                best_adv = adv
        # mild anti-stalling / anti-walk-into-corner
        return best_adv - (abs(nx - sx) + abs(ny - sy)) * 2

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        v = eval_cell(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    if best_move == [0, 0]:
        # deterministic fallback: move toward the best target by current positions
        best_r = None
        best_k = -10**18
        for rx, ry in resources:
            k = (md(ox, oy, rx, ry) - md(sx, sy, rx, ry)) * 1000 - md(sx, sy, rx, ry)
            if k > best_k:
                best_k = k
                best_r = (rx, ry)
        rx, ry = best_r
        dx = 0 if sx == rx else (1 if sx < rx else -1)
        dy = 0 if sy == ry else (1 if sy < ry else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    return best_move