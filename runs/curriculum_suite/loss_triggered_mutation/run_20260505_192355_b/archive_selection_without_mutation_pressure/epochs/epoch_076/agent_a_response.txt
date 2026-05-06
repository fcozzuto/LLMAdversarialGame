def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_eval(px, py):
        best_gap = -10**9
        best_sd = 10**9
        for rx, ry in resources:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            gap = od - sd
            if gap > best_gap or (gap == best_gap and sd < best_sd):
                best_gap = gap
                best_sd = sd
        # Prefer having a non-negative race gap; otherwise still go toward best available.
        return best_gap * 100 - best_sd

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = best_eval(nx, ny)
        # Deterministic tie-break: closer to chosen best resource for us; then favor diagonals.
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)
        elif sc == best_score:
            # Compute tie-break factors deterministically.
            # Prefer smaller min self distance among resources.
            sd = min(man(nx, ny, rx, ry) for rx, ry in resources)
            cur_sd = min(man(sx + best_move[0], sy + best_move[1], rx, ry) for rx, ry in resources)
            if sd < cur_sd or (sd == cur_sd and (abs(dx) + abs(dy) == 2) > (abs(best_move[0]) + abs(best_move[1]) == 2)):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]