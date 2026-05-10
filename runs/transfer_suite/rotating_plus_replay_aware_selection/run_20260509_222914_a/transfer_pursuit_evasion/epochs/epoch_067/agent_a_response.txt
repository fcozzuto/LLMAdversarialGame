def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    self_is_pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))
    opp_is_pursuer = not self_is_pursuer

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def apply(pos, d):
        x, y = pos
        dx, dy = d
        nx, ny = clamp(x + dx, y + dy)
        if (nx, ny) in obstacles:
            return (x, y)
        return (nx, ny)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def eval_state(spos, opos):
        d = dist(spos, opos)
        if self_is_pursuer:
            return -d + (0.01 * (spos[0] + spos[1]))
        else:
            return d + (0.01 * ((w - 1 - spos[0]) + (h - 1 - spos[1])))

    best_move = (0, 0)
    best_val = None
    for dm in moves:
        ns = apply((sx, sy), dm)
        if self_is_pursuer:
            # opponent evades: choose their move to minimize our evaluation
            worst = None
            for do in moves:
                no = apply((ox, oy), do)
                v = eval_state(ns, no)
                if worst is None or v < worst:
                    worst = v
            val = worst
        else:
            # opponent pursues: choose their move to maximize our evaluation (since opponent minimizes their objective)
            best = None
            for do in moves:
                no = apply((ox, oy), do)
                v = eval_state(ns, no)
                if best is None or v > best:
                    best = v
            val = best

        if best_val is None or val > best_val:
            best_val = val
            best_move = dm

    dx, dy = best_move
    return [int(dx), int(dy)]